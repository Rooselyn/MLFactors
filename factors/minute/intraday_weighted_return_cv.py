"""intraday_weighted_return_cv：分钟因子，单因子独立入口。"""

from factors.registry import register_factor
from factors.inputs import ParquetInput, fixed_factor
import numpy as np
import pandas as pd
from factors.base import MinuteFactor


# 分钟价乘当日复权因子；成交量(股)、成交额(元)不复权。新增月分区自动发现。
MINUTE_INPUTS = {
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", "close", date_column="trade_time", adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "adj_factor")),
    'vol': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", "vol", date_column="trade_time"),
}



def difference(values: pd.DataFrame, log: bool=False) -> pd.DataFrame:
    result = (np.log(values) if log else values).diff()
    result.iloc[[0, len(result) // 2]] = np.nan
    return result


def simple_returns(values: pd.DataFrame) -> pd.DataFrame:
    return difference(values) / values.shift(1)


def positive_int(value: int, name: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or (not 1 <= value <= maximum):
        raise ValueError(f'{name} 必须为 1 到 {maximum} 之间的整数')
    return int(value)


def panel(data: pd.DataFrame, day: pd.Timestamp, symbols: list[str], fields: tuple[str, ...], step: int=1) -> dict[str, pd.DataFrame]:
    """只取规则网格上的实际记录；5分钟取整点收盘而非桶内陈旧价格。"""
    index = grid(day, step)
    if data.empty:
        return {f: pd.DataFrame(np.nan, index=index, columns=symbols) for f in fields}
    missing = set(fields).difference(data.columns)
    if missing:
        raise KeyError(f'分钟数据缺少字段: {sorted(missing)}')
    raw = data.loc[:, list(fields)].reset_index()
    raw = raw.loc[raw.trade_time.isin(index) & raw.symbol.isin(symbols)]
    raw = raw.drop_duplicates(['trade_time', 'symbol'], keep='last')
    out = {}
    for field in fields:
        values = pd.to_numeric(raw[field], errors='coerce')
        raw[field] = values.where(np.isfinite(values) & (values.ge(0) if field in ('vol', 'amount') else values.gt(0)))
        out[field] = raw.pivot(index='trade_time', columns='symbol', values=field).reindex(index=index, columns=symbols)
    if 'high' in out and 'low' in out:
        valid = out['high'].ge(out['low'])
        for field in ('open', 'close'):
            if field in out:
                valid &= out[field].ge(out['low']) & out[field].le(out['high'])
        for field in fields:
            out[field] = out[field].where(valid)
    return out


def grid(day: pd.Timestamp, step: int=1) -> pd.DatetimeIndex:
    day = pd.Timestamp(day).normalize()
    return pd.date_range(day + pd.Timedelta(hours=9, minutes=30 + step), day + pd.Timedelta(hours=11, minutes=30), freq=f'{step}min').append(pd.date_range(day + pd.Timedelta(hours=13, minutes=step), day + pd.Timedelta(hours=15), freq=f'{step}min'))


def divide(numerator, denominator):
    return numerator / denominator.where(denominator > 0)


@register_factor
@fixed_factor('intraday_weighted_return_cv', {'min_bars': 180})
class Factor_intraday_weighted_return_cv(MinuteFactor):
    """量加权收益变异系数 (Volume-weighted return CV)."""
    MINUTE_INPUTS = MINUTE_INPUTS
    fields = ('close', 'vol')
    operation = 'weighted_return_cv'
    name = 'intraday_weighted_return_cv'
    description = '量加权收益变异系数'

    def __init__(self, min_bars: int=180) -> None:
        super().__init__(self.fields, minute_window_days=1)
        self.min_bars = positive_int(min_bars, 'min_bars', 240)

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        p = panel(minute_data, trade_date, symbols, self.minute_fields)
        valid = pd.DataFrame(True, index=grid(trade_date), columns=symbols)
        for values in p.values():
            valid &= values.notna()
        p = {key: values.where(valid) for (key, values) in p.items()}
        result = self.evaluate(p).where(valid.sum() >= self.min_bars)
        return result.replace([np.inf, -np.inf], np.nan).reindex(symbols).rename(self.name).astype(float)

    def evaluate(self, p):
        op = self.operation
        c = p['close']
        r = simple_returns(c)
        v = p['vol']
        weighted = r.abs() * v
        return divide(weighted.std(ddof=1), weighted.mean()).where(weighted.count() >= self.min_bars - 2)
