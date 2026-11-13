"""分区 Parquet 行情、指数、状态及因子输出的统一读取。"""

import glob
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


# 文件中统一保存 MLFactors/...；绝对地址仅在实际I/O时动态解析。
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_ROOT / "data" / "zz500"
DEFAULT_TRADING_STATUS_PATH = DATA_ROOT / "zz500_daily_trading_status"
DEFAULT_STOCK_DAY_PATH = DATA_ROOT / "stock_day"
DEFAULT_INDEX_PATH = DATA_ROOT / "zz500_daily_index"


def read_constituent_table(path: Path) -> pd.DataFrame:
    """只读取data/zz500内的正式逐日成分Parquet。"""
    path = resolve_data_path(path)
    if path.suffix.lower() != ".parquet":
        raise ValueError("逐日成分股必须使用data/zz500内的Parquet文件")
    frame = pd.read_parquet(path, columns=["date", "tickers"])
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    if frame.empty or frame.date.isna().any() or frame.date.duplicated().any():
        raise ValueError(f"逐日成分股日期缺失或重复: {path}")
    for value in frame.tickers:
        codes = [code.strip() for code in str(value).split(",")]
        if pd.isna(value) or not all(codes) or len(codes) != len(set(codes)):
            raise ValueError(f"逐日成分股名单为空或包含重复代码: {path}")
    return frame.sort_values("date").reset_index(drop=True)



def read_trading_status(path: Path, *, dates=None, symbols=None, symbol_aliases=None) -> pd.DataFrame:
    """读取日频状态Parquet；保留原始空值，交易方按ST/停牌缺失=False解释。"""
    columns = ["trade_date", "ts_code", "is_st", "is_suspended"]
    aliases = symbol_aliases or {}
    if symbols is not None:
        requested = {str(s) for s in symbols}
        requested.update(old for old, current in aliases.items() if current in requested)
        symbols = sorted(requested)
    frame = read_parquet_table(path, columns, dates=dates, symbols=symbols)
    frame["ts_code"] = frame.ts_code.astype("string")
    if frame[["trade_date", "ts_code"]].isna().any().any():
        raise ValueError("交易状态存在空日期或股票代码")
    if frame.duplicated(["trade_date", "ts_code"]).any():
        raise ValueError("交易状态存在重复日期/股票主键")
    for column in columns[2:]:
        frame[column] = frame[column].astype("boolean")
    if aliases:
        frame["ts_code"] = frame.ts_code.map(lambda s: aliases.get(s, s))
        frame = frame.drop_duplicates(columns)
        if frame.duplicated(["trade_date", "ts_code"]).any():
            raise ValueError("证券代码归一后存在冲突的交易状态")
    return frame.sort_values(["trade_date", "ts_code"]).reset_index(drop=True)


def normalize_dates(values: pd.Series) -> pd.Series:
    """按上海本地时间统一为无时区时间戳；YYYYMMDD 数字不当作 Unix 纳秒。"""
    if pd.api.types.is_datetime64_any_dtype(values):
        result = pd.to_datetime(values, errors="raise")
    else:
        result = pd.to_datetime(values.astype("string").str.replace(r"\.0$", "", regex=True),
                                format="mixed", errors="raise")
    if result.dt.tz is not None:
        result = result.dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
    return result


CHIP_AGGREGATIONS = ('chip_cv', 'chip_skew', 'chip_kurt', 'chip_near',
                     'chip_asym', 'chip_entropy', 'chip_tail')


def aggregate_chip_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    """按股票/日期将全部成本价档聚合为报告定义的七个日频分布统计量。"""
    keys = ['trade_date', 'ts_code']
    if frame.empty:
        return pd.DataFrame(columns=[*keys, *CHIP_AGGREGATIONS])
    if frame[keys].isna().any().any():
        raise ValueError('筹码分布缺少股票代码或交易日期')
    codes, index = pd.factorize(pd.MultiIndex.from_frame(frame[keys]), sort=True)
    n = len(index)
    price = pd.to_numeric(frame.chip_price, errors='coerce').to_numpy(dtype=float)
    weight = pd.to_numeric(frame.chip_percent, errors='coerce').to_numpy(dtype=float)
    valid = np.isfinite(price) & (price > 0) & np.isfinite(weight) & (weight >= 0)
    group, price, weight = codes[valid], price[valid], weight[valid]
    def total(value):
        return np.bincount(group, weights=value, minlength=n)
    mass = total(weight)
    with np.errstate(all='ignore'):
        mean = total(weight * price) / mass
        minimum, maximum = np.full(n, np.inf), np.full(n, -np.inf)
        positive = weight > 0
        np.minimum.at(minimum, group[positive], price[positive])
        np.maximum.at(maximum, group[positive], price[positive])
        single_price = (mass > 0) & (minimum == maximum)
        mean = np.where(single_price, minimum, mean)
        normalized = weight / mass[group]
        distance = price - mean[group]
        variance = total(normalized * distance**2)
        variance = np.where(single_price, 0, variance)
        sigma = np.sqrt(variance)
        skew = total(normalized * distance**3) / sigma**3
        kurt = total(normalized * distance**4) / variance**2
        skew = np.where((mass > 0) & (variance == 0), 0, skew)
        kurt = np.where((mass > 0) & (variance == 0), 0, kurt)
        relative = price / mean[group]
        bucket = np.searchsorted([0.7, 0.85, 0.95, 1.05, 1.15, 1.3], relative, side='left')
        bins = np.bincount(group * 7 + bucket, weights=normalized, minlength=n*7).reshape(n, 7)
        entropy = -np.where(bins > 0, bins * np.log(bins), 0).sum(axis=1)
        result = pd.DataFrame({
            'chip_cv': sigma / mean, 'chip_skew': skew, 'chip_kurt': kurt,
            'chip_near': total(normalized * (np.abs(relative-1) <= 0.03)),
            'chip_asym': total(normalized * ((price <= mean[group]).astype(float)
                                           - (price > mean[group]).astype(float))),
            'chip_entropy': entropy,
            'chip_tail': total(normalized * (np.abs(relative-1) > 0.15)),
        }, index=index)
    result.loc[mass <= 0, :] = np.nan
    result.index.names = keys
    return result.replace([np.inf, -np.inf], np.nan).reset_index()


def read_chip_distribution_table(path: str | Path, *, start=None, end=None,
                                 symbols=None) -> pd.DataFrame:
    """逐月读取并聚合，避免把所有历史价档一次载入内存。"""
    path = resolve_data_path(path)
    files = sorted(path.glob('*/*.parquet')) if path.is_dir() else sorted(Path(p) for p in glob.glob(str(path)))
    if not files:
        raise FileNotFoundError(f'未发现筹码分布分区: {path}')
    lower = pd.Timestamp(start) if start is not None else None
    upper = pd.Timestamp(end).normalize()+pd.Timedelta(days=1) if end is not None else None
    parts = []
    for file in files:
        if file.parent.name.isdigit() and len(file.parent.name) == 4 and file.stem.isdigit():
            month = pd.Period(f'{file.parent.name}-{file.stem}', freq='M')
            if upper is not None and month.start_time >= upper:
                continue
            if lower is not None and (month+1).start_time <= lower:
                continue
        frame = read_parquet_table(file, ['trade_date','ts_code','chip_price','chip_percent'],
                                   start=start, end=end, symbols=symbols)
        if not frame.empty:
            parts.append(aggregate_chip_distribution(frame))
    result = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=['trade_date','ts_code',*CHIP_AGGREGATIONS]).astype({'trade_date':'datetime64[ns]'})
    if result.duplicated(['trade_date','ts_code']).any():
        raise ValueError('筹码月分区存在重复股票/日期，不能重复计算分布')
    return result


def read_parquet_table(path: str | Path, columns, *, date_column="trade_date",
                       symbol_column="ts_code", start=None, end=None,
                       dates=None, symbols=None) -> pd.DataFrame:
    """投影读取年/月分区，按日期和代码下推过滤；只转换时间表示，不填充业务值。"""
    path = resolve_data_path(path)
    files = sorted(path.glob("*/*.parquet")) if path.is_dir() else sorted(Path(p) for p in glob.glob(str(path)))
    if not files:
        raise FileNotFoundError(f"未发现 Parquet 数据分区: {path}")
    dates = None if dates is None else pd.DatetimeIndex(dates).normalize()
    lower = pd.Timestamp(start) if start is not None else (dates.min() if dates is not None and len(dates) else None)
    upper = pd.Timestamp(end).normalize()+pd.Timedelta(days=1) if end is not None else (
        dates.max()+pd.Timedelta(days=1) if dates is not None and len(dates) else None)
    parts = []
    for file in files:
        file = resolve_data_path(file)
        if date_column in {"trade_date", "trade_time"} and file.parent.name.isdigit() and len(file.parent.name)==4 and file.stem.isdigit():
            month = pd.Period(f"{file.parent.name}-{file.stem}", freq="M")
            if upper is not None and month.start_time >= upper: continue
            if lower is not None and (month+1).start_time <= lower: continue
        date_type = pq.read_schema(file).field(date_column).type
        def boundary(value):
            value = pd.Timestamp(value)
            if pa.types.is_timestamp(date_type):
                return value.tz_localize(date_type.tz) if date_type.tz and value.tzinfo is None else value
            if pa.types.is_date(date_type): return value.date()
            if pa.types.is_integer(date_type): return int(value.strftime("%Y%m%d"))
            return value.strftime("%Y%m%d")
        predicates = []
        if dates is not None: predicates.append((date_column,"in",[boundary(d) for d in dates]))
        else:
            if lower is not None: predicates.append((date_column,">=",boundary(lower)))
            if upper is not None: predicates.append((date_column,"<",boundary(upper)))
        if symbols is not None and symbol_column:
            predicates.append((symbol_column,"in",[str(s) for s in symbols]))
        parts.append(pd.read_parquet(file, columns=list(dict.fromkeys(columns)), filters=predicates or None))
    if not parts:
        return pd.DataFrame(columns=columns).astype({date_column:"datetime64[ns]"})
    frame = pd.concat(parts, ignore_index=True)
    frame[date_column] = normalize_dates(frame[date_column])
    return frame

def resolve_project_path(value: str | Path) -> Path:
    """解析项目内资源；拒绝项目外绝对路径、父级穿越及指向外部的符号链接。"""
    path = Path(value).expanduser()
    if not path.is_absolute():
        if path.parts and path.parts[0] == "MLFactors":
            path = Path(*path.parts[1:])
        path = PROJECT_ROOT / path
    path = path.resolve()
    if not path.is_relative_to(PROJECT_ROOT.resolve()):
        raise ValueError(f"资源路径必须位于MLFactors项目内: {value}")
    return path



def resolve_data_path(value: str | Path) -> Path:
    """原始行情、财报、分钟和股票池数据只从data/zz500读取。"""
    path = resolve_project_path(value)
    if not path.is_relative_to(DATA_ROOT.resolve()):
        raise ValueError(f"原始数据路径必须位于MLFactors/data/zz500内: {value}")
    return path


def portable_path(value: str | Path) -> str:
    """项目内资源统一记录为MLFactors/...，不生成项目外路径。"""
    path = resolve_project_path(value)
    return (Path("MLFactors") / path.relative_to(PROJECT_ROOT.resolve())).as_posix()



def portable_payload(value):
    """规范化元数据/报告中的路径，保留数值、日期和模型张量。"""
    if isinstance(value, Path):
        return portable_path(value)
    if isinstance(value, dict):
        return {portable_payload(k): portable_payload(v) for k, v in value.items()}
    if isinstance(value, list):
        return [portable_payload(item) for item in value]
    if isinstance(value, tuple):
        return tuple(portable_payload(item) for item in value)
    if isinstance(value, str):
        if value.startswith("/") and "\n" not in value:
            return portable_path(value)
        # 处理Markdown及异常信息中嵌入的本项目路径。
        return value.replace(str(PROJECT_ROOT) + "/", "MLFactors/").replace(str(PROJECT_ROOT), "MLFactors")
    return value


def portable_frame(frame: pd.DataFrame) -> pd.DataFrame:
    columns = frame.select_dtypes(include=["object", "string"]).columns
    if not len(columns):
        return frame
    result = frame.copy()
    for column in columns:
        result[column] = result[column].map(portable_payload)
    return result


# 正式输出统一使用显式日期列的 Parquet，不保存 DataFrame 隐式索引。
def write_output_parquet(frame: pd.DataFrame, path: Path) -> Path:
    import os
    import uuid
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        portable_frame(frame).to_parquet(temporary, index=False)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def daily_member_mask(values: pd.DataFrame, constituents: pd.DataFrame) -> pd.DataFrame:
    """按信号日期和股票代码对齐；未知日期不能被当作非成分日。"""
    dates = pd.DatetimeIndex(pd.to_datetime(values.index))
    if constituents.empty or not dates.difference(pd.DatetimeIndex(constituents.index)).empty:
        raise ValueError("逐日成分股数据缺失，拒绝保存或回填因子值")
    mask = constituents.reindex(index=dates, columns=values.columns).fillna(False).astype(bool)
    mask.index = values.index
    return mask


def fill_member_values(values: pd.DataFrame, constituents: pd.DataFrame, seeds=None,
                       initial_value=0.0) -> pd.DataFrame:
    """逐股票统一先前向填充，再补initial_value；仅输出当日成分股。"""
    if not values.index.is_monotonic_increasing or values.index.has_duplicates:
        raise ValueError("回填日期必须有序且唯一")
    mask = daily_member_mask(values, constituents)
    clean = values.where(mask)
    if len(clean) and seeds is not None:
        clean.iloc[0] = clean.iloc[0].fillna(pd.Series(seeds).reindex(clean.columns))
    return clean.ffill().fillna(initial_value).where(mask)


def read_factor_output(directory: Path, version: str = "neutralization", *, symbols=None, start=None, end=None) -> pd.DataFrame:
    if version not in {"raw", "neutralization"}:
        raise ValueError(f"未知因子版本: {version}")
    path = Path(directory) / f"{version}.parquet"
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    if names[:2] != ["signal_date", "available_date"] or len(names) < 3:
        raise ValueError(f"因子宽表结构错误: {path}")
    columns = names if symbols is None else names[:2] + [str(c) for c in symbols if str(c) in names[2:]]
    filters = []
    if start is not None: filters.append(("signal_date", ">=", pd.Timestamp(start)))
    if end is not None: filters.append(("signal_date", "<=", pd.Timestamp(end)))
    frame = pd.read_parquet(path, columns=columns, filters=filters or None)
    if list(frame.columns[:2]) != ["signal_date", "available_date"]:
        raise ValueError(f"因子宽表结构错误: {path}")
    for column in ("signal_date", "available_date"):
        frame[column] = pd.to_datetime(frame[column], errors="raise")
    if frame.signal_date.isna().any() or frame.signal_date.duplicated().any():
        raise ValueError(f"因子信号日缺失或重复: {path}")
    return frame.sort_values("signal_date").reset_index(drop=True)


def read_weekly_output(path: Path) -> pd.DataFrame:
    """将精简的双方向宽表转换成筛选器使用的内存长表，不生成中间文件。"""
    frame = pd.read_parquet(path)
    keys = ["week_id", "week_first_trade", "week_last_trade"]
    if list(frame.columns) != keys + ["higher", "lower"]:
        raise ValueError(f"周收益结构错误: {path}")
    return frame.melt(id_vars=keys, value_vars=["higher", "lower"],
                      var_name="direction", value_name="weekly_return")
