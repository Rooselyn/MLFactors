"""按因子自有输入声明及统一分区行情计算、评估日频和分钟因子。"""

from dataloader import portable_path, portable_payload, resolve_project_path, DEFAULT_TRADING_STATUS_PATH, DEFAULT_STOCK_DAY_PATH, DEFAULT_INDEX_PATH
import argparse
import fcntl
import sys
import ast
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import importlib
import json
import multiprocessing as mp
import os
import re
import shutil
from datetime import date
from pathlib import Path
from types import SimpleNamespace
import traceback
from time import perf_counter
from typing import Any
import uuid

import numpy as np
import pandas as pd
from tqdm import tqdm

from dataloader import read_factor_output, write_output_parquet, daily_member_mask, fill_member_values
from factors_eval import (
    FactorEvalResult,
    SUMMARY_METRIC_COLUMNS,
    calc_forward_returns,
    eval as evaluate_factor,
)
from factors.base import MinuteFactor
from factors.inputs import FactorDataLoader, ParquetInput, validate_sources
from factors.registry import (
    FactorRegistry, validate_factor_ids, validate_shared_factor_ids, load_factor_configs,
    DEFAULT_BASE_FACTOR_CONFIG, DEFAULT_EXPANSION_FACTOR_CONFIG,
)
from factor_report import (build_factor_report,
                           report_directory, validate_report_config, REPORT_START, REPORT_END)
from neutralization import (
    neutralize_factor_values,
)
PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_SECURITY_STATUS_PATH = DEFAULT_TRADING_STATUS_PATH


DAILY_METRICS_PERIOD = 5
IC_DECAY_PERIODS = (5, 10, 15, 20, 40, 60)
DEFAULT_START_DATE = "2014-01-02"
REPORT_PUBLISH_DATE_COLUMN = 'available_ann_date'
FACTOR_VERSIONS = ("raw", "neutralization")
DEFAULT_FINANCIAL_FACTOR_CONFIG = (
    PROJECT_ROOT / "config" / "financial_factors.json"
)
DEFAULT_DATA_DIR = DEFAULT_STOCK_DAY_PATH
DEFAULT_MINUTE_DATA_DIR = PROJECT_ROOT / "data/zz500/stock_minute"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "zz500" / "factor_value"
DEFAULT_IC_OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "zz500" / "factor_ic"
RUNTIME_ROOT = PROJECT_ROOT / ".runtime"
UNIVERSE_SETTINGS = {
    "zz500": {"index": "000905.SH", "name": "中证500"},
}
def runtime_inputs(universe: str, *, financial: bool = False, security_status: Path = DEFAULT_SECURITY_STATUS_PATH, stock_day: Path = DEFAULT_DATA_DIR, constituents: Path | None = None) -> dict[str, ParquetInput]:
    """公共行情、股票池、交易状态与评估基准统一在运行层配置。"""
    if universe not in UNIVERSE_SETTINGS:
        raise ValueError(f"不支持的股票池: {universe}")
    sources = {
        "close_hfq": ParquetInput(portable_path(stock_day)+"/*/*.parquet", "close_hfq"),
        "total_mv": ParquetInput(portable_path(stock_day)+"/*/*.parquet", "total_mv"),
        "industry_sw_1": ParquetInput(portable_path(stock_day)+"/*/*.parquet", "industry_sw_1"),
        # 待提供各股票池的指数价格、成分及状态来源，不虚构路径或默认状态。
        "benchmark_close": (ParquetInput("MLFactors/data/zz500/zz500_daily_index/*/*.parquet", "close",
                                           date_column="trade_date", symbol_column=None, expression="close", filters=(("ts_code", "000905.SH"),))
                            if universe == "zz500" else ParquetInput(None, None, pending=True)),
        "is_member": (ParquetInput(portable_path(constituents or PROJECT_ROOT/"data/zz500/zz500_daily_constituent_stock.parquet"), "tickers",
                                     date_column="date", symbol_column=None, membership=True)
                      if universe == "zz500" else ParquetInput(None, None, pending=True)),
        "is_st": ParquetInput(portable_path(security_status), "is_st"),
        "is_suspended": ParquetInput(portable_path(security_status), "is_suspended"),
    }
    if financial:
        sources["available_ann_date"] = ParquetInput(
            "MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "f_ann_date",
            date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"),
            filters=(("report_type", "1"),), expression="coalesce(f_ann_date, ann_date)",
        )
    return sources


WINDOW_PARAM_KEYS = ("window", "lookback", "period")
HARDCODED_WARMUP_DAYS = {
    "eps_growth_63d": 63,
    "equity_growth_63d": 63,
    "net_income_growth_63d": 63,
    "revenue_growth_63d": 63,
    "reversal_20d": 20,
    "reversal_60d": 60,
    "roe_growth_63d": 63,
    "total_asset_growth_63d": 63,
    "trading_amount_20d": 20,
    "volume_60d": 60,
}


def factor_warmup_days(name: str, config: dict[str, Any]) -> int:
    """返回因子计算所需的历史交易日数。"""
    if name == "momentum_ml_252n20d":
        # 该因子会按 history_start 独立加载训练历史，避免重复加载。
        return 0
    params = config.get("params", {})
    configured = [
        int(params[key])
        for key in WINDOW_PARAM_KEYS
        if isinstance(params.get(key), int) and params[key] > 0
    ]
    base_window = max([HARDCODED_WARMUP_DAYS.get(name, 0), *configured])
    shift_days = params.get("shift_days", 0)
    if isinstance(shift_days, int) and shift_days > 0:
        base_window += shift_days
    return base_window


class Runner:
    """管理因子的数据加载、计算和结果查看。"""

    def __init__(
        self,
        factor_name: str,
        relay_class: str,
        factor_params: dict[str, Any] | None = None,
        symbols: list[str] | None = None,
        start: str | date | None = DEFAULT_START_DATE,
        end: str | date | None = None,
        data_dir: str | Path = DEFAULT_DATA_DIR,
        constituents_path: str | Path | None = None,
        forward_periods: tuple[int, ...] = IC_DECAY_PERIODS,
        ic_method: str = "rank",
        output_dir: str | Path | None = None,
        eval_price_col: str = 'close_hfq',
        security_status_path: str | Path | None = DEFAULT_SECURITY_STATUS_PATH,
        is_financial_factor: bool = False,
        factor_config: dict[str, Any] | None = None,
        universe_name: str = "中证500",
    ) -> None:
        self.factor_name = factor_name
        self.factor_config = factor_config or {
            "params": factor_params or {},
            "relay_class": relay_class,
        }
        self.universe_name = universe_name
        self.is_financial_factor = is_financial_factor
        self.forward_periods = forward_periods
        self.ic_method = ic_method
        self.eval_price_col = eval_price_col
        self.security_status_path = (
            Path(security_status_path)
            if security_status_path is not None
            else None
        )
        self.output_dir = Path(output_dir or DEFAULT_OUTPUT_ROOT / factor_name)
        self.report_output_dir = report_directory(self.output_dir)
        universe = "zz1000" if universe_name == "中证1000" else "zz500"
        self.ic_output_dir = PROJECT_ROOT / "outputs" / universe / "factor_ic" / factor_name
        self.factor = FactorRegistry.get(relay_class)(**(factor_params or {}))
        self.data = pd.DataFrame()
        self.result = pd.DataFrame()
        self.raw_result = pd.DataFrame()
        self.neutralized_result = pd.DataFrame()
        self.evaluations: dict[str, dict[int, FactorEvalResult]] = {}
        self.summary = pd.DataFrame()
        self.data_loader = FactorDataLoader(
            self.factor, start=start, end=end, symbols=symbols,
            runtime_inputs=runtime_inputs(universe, financial=self.is_financial_factor and not getattr(self.factor, "PRESERVE_REPORT_HISTORY", False),
                                          security_status=self.security_status_path or DEFAULT_SECURITY_STATUS_PATH,
                                          stock_day=Path(data_dir), constituents=constituents_path),
            universe=universe,
            warmup_days=max(factor_warmup_days(factor_name, self.factor_config),
                            getattr(self.factor, "warmup_days", 0),
                            getattr(self.factor, "minute_window_days", 1)-1),
        )
        if hasattr(self.factor, "history_loader"):
            self.factor.history_loader = self.data_loader.load_history

    def calculate(self,
                  combined_data: pd.DataFrame | None = None,
                  save: bool = False) -> pd.DataFrame:
        """计算因子；save=True 时保存双版本Parquet宽表。"""
        data = self.data if combined_data is None else combined_data
        if data is None or data.empty:
            raise ValueError("没有可用于计算因子的 combined_data")

        if isinstance(self.factor, MinuteFactor):
            signals = self.factor.generate_minute_signals(data, self.data_loader)
        else:
            signals = self.factor.generate_signals(data, None)
        available = getattr(self.factor, "available_ann_dates", None)
        if available is not None:
            data = data.copy()
            data[REPORT_PUBLISH_DATE_COLUMN] = available.rename_axis(index="date", columns="symbol").stack(future_stack=True).reindex(data.index)
            if combined_data is None:
                self.data = data
        # Undefined arithmetic is missing data, never a tradeable +/-inf.
        # Apply this before neutralization and saving, including legacy bases.
        signals = signals.replace([np.inf, -np.inf], np.nan)
        signals = self.data_loader.filter_signals_to_universe(signals)
        neutralized_signals = neutralize_factor_values(signals, data)
        self.result = signals
        self.raw_result = signals
        self.neutralized_result = neutralized_signals
        if save:
            self.save_signals(
                signals,
                neutralized_signals=neutralized_signals,
                combined_data=data,
            )
        return signals

    def save_signals(self, signals, combined_data=None, neutralized_signals=None) -> Path:
        """保存两个版本的日期×股票宽表，日期为显式列。"""
        data = self.data if combined_data is None else combined_data
        if data is None or data.empty:
            raise ValueError("没有可用于保存因子值的数据")
        signals = signals.where(daily_member_mask(signals, self.data_loader.constituents))
        if neutralized_signals is None:
            neutralized_signals = neutralize_factor_values(signals, data)
        symbols = pd.Index(signals.columns).intersection(data.index.get_level_values("symbol").unique(), sort=False)
        if not self.data_loader.constituents.empty:
            members = self.data_loader.constituents.reindex(index=signals.index, columns=symbols, fill_value=False).any(axis=0)
            symbols = symbols[members.to_numpy()]
        calendar = self.data_loader.trading_calendar
        if calendar.empty:
            calendar = pd.DatetimeIndex(data.index.get_level_values("date").unique()).sort_values()
        available = pd.Series(calendar[1:].to_numpy(), index=calendar[:-1])
        for version, values in (("raw", signals), ("neutralization", neutralized_signals)):
            frame = values.reindex(index=signals.index, columns=symbols).copy().sort_index()
            frame = frame.where(daily_member_mask(frame, self.data_loader.constituents))
            frame.index = pd.to_datetime(frame.index)
            frame.columns = frame.columns.astype(str)
            frame.insert(0, "available_date", frame.index.map(available))
            frame.index.name = "signal_date"
            write_output_parquet(frame.reset_index(), self.output_dir / f"{version}.parquet")
        return self.output_dir

    def evaluate(
        self,
        combined_data: pd.DataFrame,
        signals: pd.DataFrame,
        forward_periods: tuple[int, ...] | None = None,
    ) -> tuple[dict[int, FactorEvalResult], pd.DataFrame]:
        """计算指定周期的因子评估结果。"""
        periods = forward_periods or self.forward_periods
        evaluations = {
            period: evaluate_factor(
                signals,
                combined_data,
                forward_period=period,
                ic_method=self.ic_method,
                price_col=self.eval_price_col,
                forward_returns=getattr(self,"report_forward_returns",{}).get(period),
            )
            for period in periods
        }
        summary = pd.concat(
            [evaluation.summary for evaluation in evaluations.values()]
        ).sort_index()
        return evaluations, summary

    @staticmethod
    def _suffix_metrics(frame: pd.DataFrame, version: str) -> pd.DataFrame:
        """Append a factor-value version suffix to every metric column."""
        return frame.rename(
            columns={column: f"{column}_{version}" for column in frame.columns}
        )

    def evaluate_versions(
        self,
        combined_data: pd.DataFrame,
        signal_versions: dict[str, pd.DataFrame],
        forward_periods: tuple[int, ...] | None = None,
    ) -> tuple[dict[str, dict[int, FactorEvalResult]], pd.DataFrame]:
        """Evaluate raw and neutralized factor values with identical settings."""
        missing_versions = set(FACTOR_VERSIONS).difference(signal_versions)
        if missing_versions:
            raise ValueError(
                "因子值缺少版本: " + ", ".join(sorted(missing_versions))
            )

        evaluations: dict[str, dict[int, FactorEvalResult]] = {}
        summaries = []
        for version in FACTOR_VERSIONS:
            version_evaluations, version_summary = self.evaluate(
                combined_data,
                signal_versions[version],
                forward_periods=forward_periods,
            )
            unexpected = set(version_summary.columns).difference(
                SUMMARY_METRIC_COLUMNS
            )
            missing = set(SUMMARY_METRIC_COLUMNS).difference(
                version_summary.columns
            )
            if unexpected or missing:
                raise ValueError(
                    f"{version} 回测汇总字段不符合约定；"
                    f"缺少={sorted(missing)}，额外={sorted(unexpected)}"
                )
            evaluations[version] = version_evaluations
            summaries.append(self._suffix_metrics(version_summary, version))

        summary = pd.concat(summaries, axis=1).sort_index()
        return evaluations, summary


    def save_daily_ic(self, evaluations, output_path: Path) -> Path:
        """保存5日未来收益口径的双版本逐日Rank IC；可用日与因子值相同。"""
        calendar = self.data_loader.trading_calendar
        if calendar.empty:
            calendar = pd.DatetimeIndex(self.data.index.get_level_values("date").unique()).sort_values()
        available = pd.Series(calendar[1:].to_numpy(), index=calendar[:-1])
        output_path = Path(output_path)
        for version in FACTOR_VERSIONS:
            evaluation = evaluations.get(version, {}).get(DAILY_METRICS_PERIOD)
            if evaluation is None:
                raise ValueError(f"{version} 缺少5日未来收益口径IC")
            series = evaluation.full_ic_series.copy().sort_index()
            series = series.loc[(series.index >= REPORT_START) & (series.index <= REPORT_END)]
            series.index = pd.to_datetime(series.index)
            frame = series.rename(f"IC_{version}").rename_axis("signal_date").reset_index()
            frame.insert(1, "available_date", frame.signal_date.map(available))
            write_output_parquet(frame, output_path / f"{version}.parquet")
        return output_path


    def latest(self, version: str = "raw") -> pd.Series:
        """返回指定版本最近一个有因子结果的交易日。"""
        if version not in FACTOR_VERSIONS:
            raise ValueError(f"未知因子版本: {version}")
        source = (
            self.raw_result if version == "raw" else self.neutralized_result
        )
        latest_result = source.dropna(how="all")
        if latest_result.empty:
            return pd.Series(dtype=float, name=f"{self.factor_name}_{version}")
        result = latest_result.iloc[-1].dropna().sort_values()
        result.name = latest_result.index[-1]
        return result

    def run(self, build_report: bool = True) -> dict[str,dict[int,FactorEvalResult]]:
        """因子值→每日IC→精细自然周收益→MD及交互HTML。"""
        if build_report:
            validate_report_config(self.factor_name, self.factor_config)
        timer=perf_counter()
        print(f'FACTOR_STAGE factor={self.factor_name} stage=values status=start',flush=True)
        self.data=self.data_loader.load_all(apply_universe_filters=False)
        self.calculate(save=True)
        print(f'FACTOR_STAGE factor={self.factor_name} stage=values status=done seconds={perf_counter()-timer:.2f}',flush=True)
        if not build_report:return {}
        timer=perf_counter()
        signals={"raw":self.raw_result,"neutralization":self.neutralized_result}
        self.evaluations,self.summary=self.evaluate_versions(self.data,signals,forward_periods=(5,))
        self.save_daily_ic(self.evaluations,self.ic_output_dir)
        print(f'FACTOR_STAGE factor={self.factor_name} stage=ic status=done seconds={perf_counter()-timer:.2f}',flush=True)
        timer=perf_counter()
        engine=_load_return_engine()
        context=engine.build_market_context(
            constituents_path=WEEKLY_CONSTITUENTS,status_path=self.security_status_path,
            execution_prices=getattr(self,"execution_prices",engine.DEFAULT_EXECUTION_PRICES),
            benchmark_path=getattr(self,"return_benchmark",engine.DEFAULT_BENCHMARK),
            start=str(REPORT_START.date()),end=str(min(REPORT_END,pd.Timestamp(self.data.index.get_level_values("date").max())).date()))
        self.return_output_dir=getattr(self,"return_output_dir",self.output_dir.parents[1]/"factor_return"/self.factor_name)
        engine.run_report_backtests(factor_name=self.factor_name,
            factor_frame=read_factor_output(self.output_dir,"neutralization"),
            raw_factor_frame=read_factor_output(self.output_dir,"raw"),market_data=self.data,
            context=context,output_dir=self.return_output_dir)
        print(f'FACTOR_STAGE factor={self.factor_name} stage=returns status=done seconds={perf_counter()-timer:.2f}',flush=True)
        timer=perf_counter()
        build_factor_report(self,signals,self.factor_config,self.return_output_dir)
        print(f'FACTOR_STAGE factor={self.factor_name} stage=report status=done seconds={perf_counter()-timer:.2f}',flush=True)
        return self.evaluations


# ---------------------------------------------------------------------------
# Full daily-factor pipeline
# ---------------------------------------------------------------------------

_PIPELINE_CONFIGS: dict[str, dict[str, Any]] = {}
_PIPELINE_REUSE_BASE_VALUES = False
_PIPELINE_BASE_CONFIGS: dict[str, dict[str, Any]] = {}
_PIPELINE_MARKET_DATA: pd.DataFrame | None = None
_PIPELINE_CALENDAR = pd.DatetimeIndex([])
_PIPELINE_CONSTITUENTS = pd.DataFrame()
_PIPELINE_DATES = pd.DatetimeIndex([])
_PIPELINE_SYMBOLS: list[str] = []
_PIPELINE_WORK_DIR: Path | None = None
_PIPELINE_OUTPUT_ROOT = DEFAULT_OUTPUT_ROOT
_PIPELINE_IC_OUTPUT_ROOT = DEFAULT_IC_OUTPUT_ROOT
_PIPELINE_FILL_SEED_ROOT: Path | None = None
_PIPELINE_INCREMENTAL_START: pd.Timestamp | None = None
_PIPELINE_FINANCIAL_FACTORS: set[str] = set()
_PIPELINE_UNIVERSE_NAME = "中证500"
_PIPELINE_DATA_DIR = DEFAULT_DATA_DIR
_PIPELINE_CONSTITUENT_INDEX = "000905.SH"
_PIPELINE_RETURN_OUTPUT_ROOT = PROJECT_ROOT / "outputs/zz500/factor_return"
_PIPELINE_REPORT_CONTEXT = None
_PIPELINE_FORWARD_PANELS: dict[int, pd.DataFrame] = {}


def _pipeline_result(name: str, status: str, **extra: Any) -> dict[str, Any]:
    return {"factor": name, "status": status, **extra}


def _run_parallel(
    function: Any,
    items: list[Any],
    workers: int,
    description: str,
) -> None:
    failures = []
    context = mp.get_context("fork")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        futures = {executor.submit(function, item): item for item in items}
        for future in tqdm(
            as_completed(futures), total=len(futures), desc=description, unit="factor"
        ):
            result = future.result()
            if result["status"] == "failed":
                failures.append(result)
                tqdm.write(f"FAILED {result['factor']}\n{result['traceback']}")
    if failures:
        raise RuntimeError(f"{description}失败: {len(failures)}")


def _factor_values_ready(output_root: Path, name: str) -> bool:
    """校验已有基础因子的双版本Parquet元信息及日期网格。"""
    import pyarrow.parquet as pq
    try:
        paths = [output_root / name / f"{v}.parquet" for v in FACTOR_VERSIONS]
        schemas = [pq.read_schema(path).names for path in paths]
        if schemas[0] != schemas[1] or schemas[0][:2] != ["signal_date", "available_date"] or len(schemas[0]) < 3:
            return False
        dates = [pd.read_parquet(path, columns=["signal_date", "available_date"]) for path in paths]
        return (not dates[0].empty and dates[0].equals(dates[1])
                and dates[0].signal_date.notna().all()
                and not dates[0].signal_date.duplicated().any())
    except (OSError, ValueError):
        return False


def _calculate_base_values(
    task: tuple[str, dict[str, Any], str, str | None, str]
) -> dict[str, Any]:
    name, config, start, end, output_root_text = task
    try:
        importlib.import_module(config["module"])
        output_root = Path(output_root_text)
        runner = Runner(
            factor_name=name,
            relay_class=config["relay_class"],
            factor_params=config.get("params", {}),
            start=start,
            end=end,

            data_dir=_PIPELINE_DATA_DIR,
            constituents_path=(WEEKLY_CONSTITUENTS if _PIPELINE_CONSTITUENT_INDEX == "000905.SH" else _PIPELINE_DATA_DIR / "constituents_daily.parquet"),
            output_dir=output_root / name,
            is_financial_factor=name in _PIPELINE_FINANCIAL_FACTORS,
            factor_config=config,
            universe_name=_PIPELINE_UNIVERSE_NAME,

        )
        runner.run(build_report=False)
        return _pipeline_result(name, "completed")
    except Exception:
        return _pipeline_result(name, "failed", traceback=traceback.format_exc())


def _robust_z(values: np.ndarray) -> np.ndarray:
    with np.errstate(all="ignore"):
        median = np.nanmedian(values, axis=1, keepdims=True)
        mad = np.nanmedian(np.abs(values - median), axis=1, keepdims=True)
        scale = 1.4826 * mad
        fallback = np.nanstd(values, axis=1, keepdims=True)
        scale = np.where(np.isfinite(scale) & (scale > 1e-12), scale, fallback)
        result = (values - median) / np.where(scale > 1e-12, scale, np.nan)
    return np.clip(result, -5.0, 5.0).astype("float32")


def _atomic_save_npy(path: Path, values: np.ndarray) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("wb") as file:
        np.save(file, values, allow_pickle=False)
    temporary.replace(path)


def _matrix_path(name: str, version: str, standardized: bool = False) -> Path:
    assert _PIPELINE_WORK_DIR is not None
    prefix = "z_" if standardized else ""
    return _PIPELINE_WORK_DIR / "base_matrices" / f"{name}__{prefix}{version}.npy"


def _load_saved_versions(name: str) -> dict[str, pd.DataFrame]:
    return {version: read_factor_output(_PIPELINE_OUTPUT_ROOT / name, version, symbols=_PIPELINE_SYMBOLS, start=_PIPELINE_DATES.min(), end=_PIPELINE_DATES.max())
            .drop(columns="available_date").set_index("signal_date")
            .reindex(index=_PIPELINE_DATES, columns=_PIPELINE_SYMBOLS)
            .rename_axis(index="date", columns="symbol")
            for version in FACTOR_VERSIONS}


def _build_base_matrix(name: str) -> dict[str, Any]:
    try:
        versions = _load_saved_versions(name)
        for version, frame in versions.items():
            frame = frame.where(daily_member_mask(frame, _PIPELINE_CONSTITUENTS))
            if _PIPELINE_REUSE_BASE_VALUES:
                # 扩展专用流程只在内存回填，基础Parquet始终只读。
                frame = fill_member_values(frame, _PIPELINE_CONSTITUENTS)
            values = frame.to_numpy(dtype="float32")
            _atomic_save_npy(_matrix_path(name, version), values)
            _atomic_save_npy(_matrix_path(name, version, standardized=True), _robust_z(values))
        return _pipeline_result(name, "completed")
    except Exception:
        return _pipeline_result(name, "failed", traceback=traceback.format_exc())


def _eval_formula_ast(node: ast.AST, variables: dict[str, np.ndarray]) -> np.ndarray:
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in {"ABS", "SOFT", "POS"}
            and len(node.args) == 1 and not node.keywords):
        value = _eval_formula_ast(node.args[0], variables)
        if node.func.id == "ABS": return np.abs(value)
        if node.func.id == "SOFT": return value / (1.0 + np.abs(value))
        return np.maximum(value, 0.0)
    if isinstance(node, ast.Expression):
        return _eval_formula_ast(node.body, variables)
    if isinstance(node, ast.Name) and node.id in variables:
        return variables[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return np.asarray(float(node.value), dtype="float32")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _eval_formula_ast(node.operand, variables)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left = _eval_formula_ast(node.left, variables)
        right = _eval_formula_ast(node.right, variables)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
    raise ValueError(f"派生公式包含不允许的语法: {ast.dump(node)}")


def _load_base_matrix(name: str, role: str, version: str) -> np.ndarray:
    standardized = role in {"Z", "S"}
    return np.load(_matrix_path(name, version, standardized), mmap_mode="r")


def _evaluate_combination(params: dict[str, Any], version: str) -> np.ndarray:
    directions = dict(zip(params["input_factors"], params["input_directions"]))
    variables: dict[str, np.ndarray] = {}
    counter = 0

    def replace_token(match: re.Match[str]) -> str:
        nonlocal counter
        role, factor_name = match.group(1), match.group(2)
        if factor_name not in directions:
            raise ValueError(f"公式引用未声明的基础因子: {factor_name}")
        variable = f"v{counter}"
        counter += 1
        values = _load_base_matrix(factor_name, role, version)
        variables[variable] = directions[factor_name] * values if role == "S" else values
        return variable

    expression = params["formula"].replace("×", "*")
    expression = re.sub(r"([0-9.]+)\[", r"\1*[", expression)
    expression = re.sub(r"(?<![A-Za-z_])([XZS])\(([^)]+)\)", replace_token, expression)
    expression = expression.replace("[", "(").replace("]", ")")
    expression = re.sub(r"(?<=[0-9.)])(?=v\d+)", "*", expression)
    with np.errstate(all="ignore"):
        return np.asarray(
            _eval_formula_ast(ast.parse(expression, mode="eval"), variables),
            dtype="float32",
        )


def _evaluate_transform(params: dict[str, Any], version: str) -> np.ndarray:
    values = np.asarray(
        _load_base_matrix(params["input_factors"][0], "Z", version), dtype="float32"
    )
    code = params["transformation"]
    with np.errstate(all="ignore"):
        if code == "T01":
            result = np.where(values == 0, np.nan, 1.0 / (values + 1e-6 * np.sign(values)))
        elif code == "T02": result = np.abs(values)
        elif code == "T03": result = np.maximum(values, 0)
        elif code == "T04": result = np.maximum(-values, 0)
        elif code == "T05": result = -np.abs(values - 1)
        elif code == "T06": result = -np.abs(values + 1)
        elif code == "T07": result = values / (1 + values**2)
        elif code == "T08": result = values * (np.abs(values) >= 1)
        elif code == "T09": result = values * (np.abs(values) < 1)
        elif code == "T10": result = np.abs(values) * (1 + 0.5 * (values > 0))
        elif code == "T11": result = np.sign(values) * (np.abs(values) >= 1)
        elif code == "T12": result = -np.abs(values**2 - 1)
        else: raise ValueError(f"未知单因子变换: {code}")
    result = np.asarray(result, dtype="float32")
    result[~np.isfinite(values)] = np.nan
    return result


def _make_memory_runner(name: str, config: dict[str, Any]) -> Runner:
    assert _PIPELINE_MARKET_DATA is not None
    runner = Runner.__new__(Runner)
    runner.factor_name = name
    runner.factor_config = config
    runner.universe_name = _PIPELINE_UNIVERSE_NAME
    runner.is_financial_factor = any(
        value in _PIPELINE_FINANCIAL_FACTORS
        for value in config.get("params", {}).get("input_factors", [name])
    )
    runner.forward_periods = IC_DECAY_PERIODS
    runner.ic_method = "rank"
    runner.eval_price_col = 'close_hfq'
    runner.security_status_path = DEFAULT_SECURITY_STATUS_PATH
    runner.output_dir = _PIPELINE_OUTPUT_ROOT / name
    runner.report_output_dir = report_directory(runner.output_dir)
    runner.return_output_dir = _PIPELINE_RETURN_OUTPUT_ROOT / name
    runner.report_forward_returns = _PIPELINE_FORWARD_PANELS
    runner.data = _PIPELINE_MARKET_DATA
    runner.result = pd.DataFrame()
    runner.raw_result = pd.DataFrame()
    runner.neutralized_result = pd.DataFrame()
    runner.evaluations = {}
    runner.summary = pd.DataFrame()
    runner.data_loader = SimpleNamespace(
        trading_calendar=_PIPELINE_CALENDAR,
        constituents=_PIPELINE_CONSTITUENTS,
    )
    return runner


def _calculate_derived_values(name: str) -> dict[str, Any]:
    try:
        config = _PIPELINE_CONFIGS[name]
        params = config["params"]
        arrays = {}
        for version in FACTOR_VERSIONS:
            values = (
                _evaluate_transform(params, version)
                if params["expansion_kind"] == "single_transform"
                else _evaluate_combination(params, version)
            )
            arrays[version] = pd.DataFrame(
                values, index=_PIPELINE_DATES, columns=_PIPELINE_SYMBOLS, dtype="float32"
            ).rename_axis(index="date", columns="symbol")
        arrays["neutralization"] = neutralize_factor_values(
            arrays["neutralization"], _PIPELINE_MARKET_DATA
        ).astype("float32")
        runner = _make_memory_runner(name, config)
        runner.save_signals(
            arrays["raw"],
            combined_data=_PIPELINE_MARKET_DATA,
            neutralized_signals=arrays["neutralization"],
        )
        return _pipeline_result(name, "completed")
    except Exception:
        return _pipeline_result(name, "failed", traceback=traceback.format_exc())


def _read_last_factor_values_before(path: Path, cutoff: pd.Timestamp, columns: list[str]) -> dict[str, float]:
    if not path.is_file():
        return dict.fromkeys(columns, np.nan)
    frame = read_factor_output(path.parent, path.stem, symbols=columns, end=cutoff - pd.Timedelta(nanoseconds=1))
    values = frame.set_index("signal_date").reindex(columns=columns)
    values = values.where(daily_member_mask(values, _PIPELINE_CONSTITUENTS))
    frame[columns] = values.to_numpy()
    if frame.empty:
        return dict.fromkeys(columns, np.nan)
    interval = _PIPELINE_CONSTITUENTS.loc[
        (_PIPELINE_CONSTITUENTS.index >= frame.signal_date.iloc[-1]) &
        (_PIPELINE_CONSTITUENTS.index < cutoff)
    ].reindex(columns=columns).fillna(False)
    return {c: (pd.to_numeric(frame[c], errors="coerce").iloc[-1]
                if c in frame and interval[c].all() else np.nan) for c in columns}


def _fill_factor_values(name: str) -> dict[str, Any]:
    try:
        changed = cells = 0
        for version in FACTOR_VERSIONS:
            path = _PIPELINE_OUTPUT_ROOT / name / f"{version}.parquet"
            frame = read_factor_output(path.parent, version)
            columns = list(frame.columns[2:])
            eligible = pd.Series(True, index=frame.index) if _PIPELINE_INCREMENTAL_START is None else frame.signal_date.ge(_PIPELINE_INCREMENTAL_START)
            if not eligible.any():
                continue
            values = frame.loc[eligible, columns].apply(pd.to_numeric, errors="coerce")
            seeds = dict.fromkeys(columns, np.nan)
            if _PIPELINE_FILL_SEED_ROOT is not None and _PIPELINE_INCREMENTAL_START is not None:
                seeds = _read_last_factor_values_before(_PIPELINE_FILL_SEED_ROOT / name / path.name, _PIPELINE_INCREMENTAL_START, columns)
            values.index = pd.DatetimeIndex(frame.loc[eligible, "signal_date"])
            mask = daily_member_mask(values, _PIPELINE_CONSTITUENTS)
            filled = fill_member_values(values, _PIPELINE_CONSTITUENTS, seeds)
            count = int((values.isna() & mask).sum().sum())
            if count or (values.notna() & ~mask).any().any():
                frame.loc[eligible, columns] = filled.to_numpy()
                write_output_parquet(frame, path)
                changed += 1
                cells += count
        return _pipeline_result(name, "completed", files_changed=changed, cells_filled=cells)
    except Exception:
        return _pipeline_result(name, "failed", traceback=traceback.format_exc())


def _build_markdown_report(name: str) -> dict[str, Any]:
    try:
        config = _PIPELINE_CONFIGS[name]
        frames={v:read_factor_output(_PIPELINE_OUTPUT_ROOT/name,v) for v in FACTOR_VERSIONS}
        signals={v:frame.drop(columns="available_date").set_index("signal_date").rename_axis("date")
                 for v,frame in frames.items()}
        runner = _make_memory_runner(name, config)
        runner.report_factor_frame=frames["neutralization"]
        runner.report_raw_factor_frame=frames["raw"]
        runner.neutralized_result = signals["neutralization"]
        build_factor_report(runner, signals, config, runner.return_output_dir)
        return _pipeline_result(name, "completed")
    except Exception:
        return _pipeline_result(name, "failed", traceback=traceback.format_exc())


def _build_daily_ic(name: str) -> dict[str, Any]:
    """生成流水线的双版本逐日IC。"""
    try:
        config = _PIPELINE_CONFIGS[name]
        signals = _load_saved_versions(name)
        runner = _make_memory_runner(name, config)
        runner.raw_result = signals["raw"]
        runner.neutralized_result = signals["neutralization"]
        evaluations, _ = runner.evaluate_versions(
            _PIPELINE_MARKET_DATA,
            signals,
            forward_periods=(DAILY_METRICS_PERIOD,),
        )
        runner.save_daily_ic(
            evaluations,
            _PIPELINE_IC_OUTPUT_ROOT / name,
        )
        return _pipeline_result(name, "completed")
    except Exception:
        return _pipeline_result(name, "failed", traceback=traceback.format_exc())


def _build_report_returns(name: str) -> dict[str, Any]:
    try:
        frame=read_factor_output(_PIPELINE_OUTPUT_ROOT/name,"neutralization")
        return _load_return_engine().run_report_backtests(
            factor_name=name,factor_frame=frame,raw_factor_frame=read_factor_output(_PIPELINE_OUTPUT_ROOT/name,"raw"),
            market_data=_PIPELINE_MARKET_DATA,
            context=_PIPELINE_REPORT_CONTEXT,output_dir=_PIPELINE_RETURN_OUTPUT_ROOT/name)
    except Exception:
        return _pipeline_result(name,"failed",traceback=traceback.format_exc())


def _run_report_stages(names: list[str], workers: int, *,
                       execution_prices: Path | None = None, benchmark: Path | None = None,
                       security_status: Path = DEFAULT_SECURITY_STATUS_PATH,
                       constituents_path: Path | None = None) -> None:
    """全体每日IC完成→全体精细收益完成→全体MD及HTML，阶段之间严格屏障。"""
    global _PIPELINE_REPORT_CONTEXT, _PIPELINE_FORWARD_PANELS
    data=_PIPELINE_MARKET_DATA
    if data is None or data.empty:raise ValueError("报告阶段缺少共享行情")
    engine=_load_return_engine()
    start=max(REPORT_START,pd.Timestamp(data.index.get_level_values('date').min()))
    end=min(REPORT_END,pd.Timestamp(data.index.get_level_values('date').max()))
    if start >= end:raise ValueError("报告阶段缺少有效统计区间")
    _PIPELINE_FORWARD_PANELS={h:calc_forward_returns(data,h,price_col='close_hfq').unstack('symbol')
                             for h in IC_DECAY_PERIODS}
    print(f'DAILY_IC_START factors={len(names)} workers={workers}',flush=True)
    _run_parallel(_build_daily_ic,names,workers,'逐日IC')
    print(f'DAILY_IC_DONE completed={len(names)}',flush=True)
    _PIPELINE_REPORT_CONTEXT=engine.build_market_context(
        constituents_path=constituents_path or WEEKLY_CONSTITUENTS,status_path=security_status,
        execution_prices=execution_prices or engine.DEFAULT_EXECUTION_PRICES,
        benchmark_path=benchmark or engine.DEFAULT_BENCHMARK,
        start=str(start.date()),end=str(end.date()))
    print(f'WEEKLY_RETURNS_START factors={len(names)} workers={workers}',flush=True)
    _run_parallel(_build_report_returns,names,workers,'精细自然周收益及报告组合')
    print(f'WEEKLY_RETURNS_DONE completed={len(names)}',flush=True)
    print(f'REPORT_START factors={len(names)} workers={workers}',flush=True)
    _run_parallel(_build_markdown_report,names,workers,'MD和HTML报告')
    print(f'REPORT_DONE completed={len(names)}',flush=True)


def _validate_full_config(
    full_configs: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """校验内存中合并的配置，并拆出基础与扩展因子。"""
    validate_factor_ids(full_configs)
    base_configs = {
        name: config
        for name, config in full_configs.items()
        if not config.get("params", {}).get("expansion_kind")
    }
    if not base_configs:
        raise ValueError("缺少基础因子配置")
    derived = []
    for name, config in full_configs.items():
        if name in base_configs:
            continue
        params = config.get("params", {})
        kind = params.get("expansion_kind")
        required = {"formula", "input_factors", "input_directions"}
        if kind == "single_transform": required.add("transformation")
        elif kind != "factor_combination":
            raise ValueError(f"{name} 缺少有效 expansion_kind")
        missing = sorted(required.difference(params))
        if missing: raise ValueError(f"{name} 派生配置不完整: {missing}")
        if not set(params["input_factors"]).issubset(base_configs):
            raise ValueError(f"{name} 引用了非基础输入")
        if len(params["input_factors"]) != len(params["input_directions"]):
            raise ValueError(f"{name} 输入方向数量不一致")
        derived.append(name)
    return base_configs, sorted(derived)


def run_full_pipeline(
    expansion_config_path: Path,
    base_config_path: Path,
    output_root: Path,
    ic_output_root: Path,
    data_dir: Path,
    constituent_index: str,
    universe: str,
    start: str,
    end: str | None,
    workers: int,
    fill_seed_root: Path | None,
    return_output_root: Path | None = None,
    execution_prices: Path | None = None,
    return_benchmark: Path | None = None,
    security_status: Path = DEFAULT_SECURITY_STATUS_PATH,
    expansion_only: bool = False,
    expansion_start: int = 1,
) -> None:
    """全部因子值及回填→每日IC→精细自然周收益→独立MD及交互HTML。"""
    global _PIPELINE_CONFIGS, _PIPELINE_BASE_CONFIGS, _PIPELINE_MARKET_DATA
    global _PIPELINE_CALENDAR, _PIPELINE_CONSTITUENTS
    global _PIPELINE_DATES
    global _PIPELINE_SYMBOLS, _PIPELINE_WORK_DIR, _PIPELINE_OUTPUT_ROOT
    global _PIPELINE_IC_OUTPUT_ROOT, _PIPELINE_FILL_SEED_ROOT
    global _PIPELINE_INCREMENTAL_START
    global _PIPELINE_FINANCIAL_FACTORS
    global _PIPELINE_DATA_DIR
    global _PIPELINE_CONSTITUENT_INDEX, _PIPELINE_UNIVERSE_NAME
    global _PIPELINE_RETURN_OUTPUT_ROOT
    global _PIPELINE_REUSE_BASE_VALUES

    workers = max(1, workers)
    _PIPELINE_CONFIGS = load_factor_configs(base_config_path, expansion_config_path)
    if "momentum_ml_252n20d" in _PIPELINE_CONFIGS:
        _PIPELINE_CONFIGS["momentum_ml_252n20d"].setdefault("params", {})[
            "universe"
        ] = universe
    _PIPELINE_BASE_CONFIGS, derived_names = _validate_full_config(_PIPELINE_CONFIGS)
    _PIPELINE_REUSE_BASE_VALUES = expansion_only
    if expansion_only:
        derived_names = [name for name in derived_names if int(name.rsplit('_', 1)[1]) >= expansion_start]
        if not derived_names:
            raise ValueError("所选扩展因子范围为空")
        with ThreadPoolExecutor(max_workers=min(workers, 16)) as executor:
            base_ready = list(executor.map(
                lambda name: _factor_values_ready(output_root, name), _PIPELINE_BASE_CONFIGS))
        missing = [name for name, ready in zip(_PIPELINE_BASE_CONFIGS, base_ready) if not ready]
        if missing:
            raise FileNotFoundError(f"基础因子值缺少或无效，扩展专用流程禁止重算: {missing[:10]}")
        print(f"BASE_VALUES_REUSED factors={len(_PIPELINE_BASE_CONFIGS)} read_only=True "
              f"expansions={len(derived_names)} workers={workers}", flush=True)
    for name in (derived_names if expansion_only else _PIPELINE_CONFIGS):
        validate_report_config(name, _PIPELINE_CONFIGS[name])
    # 在建输出目录及派生任务之前检查占位声明，避免半途失败留下运行目录。
    for name, config in ({} if expansion_only else _PIPELINE_BASE_CONFIGS).items():
        factor = FactorRegistry.get(config["relay_class"])(**config.get("params", {}))
        validate_sources(factor.INPUTS)
    validate_sources(runtime_inputs(universe, financial=not expansion_only, security_status=security_status))
    financial = json.loads(DEFAULT_FINANCIAL_FACTOR_CONFIG.read_text(encoding="utf-8"))
    _PIPELINE_FINANCIAL_FACTORS = set(financial["factor_names"])
    _PIPELINE_DATA_DIR = data_dir.resolve()
    _PIPELINE_CONSTITUENT_INDEX = constituent_index
    _PIPELINE_UNIVERSE_NAME = str(UNIVERSE_SETTINGS[universe]["name"])
    _PIPELINE_OUTPUT_ROOT = output_root.resolve()
    _PIPELINE_RETURN_OUTPUT_ROOT = (return_output_root or output_root.parent/"factor_return").resolve()
    _PIPELINE_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    _PIPELINE_IC_OUTPUT_ROOT = ic_output_root.resolve()
    _PIPELINE_IC_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    _PIPELINE_FILL_SEED_ROOT = (
        fill_seed_root.resolve() if fill_seed_root is not None else None
    )
    _PIPELINE_INCREMENTAL_START = (
        pd.Timestamp(start) if _PIPELINE_FILL_SEED_ROOT is not None else None
    )
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    _PIPELINE_WORK_DIR = RUNTIME_ROOT / f"factor_pipeline_{uuid.uuid4().hex}"
    (_PIPELINE_WORK_DIR / "base_matrices").mkdir(parents=True)

    try:
        # 扩展因子直接使用运行层公共数据，不依附某个基础因子。
        loader = FactorDataLoader(
            runtime_inputs=runtime_inputs(universe, financial=not expansion_only, security_status=security_status), universe=universe,
            start=start, end=end, context_only=True,
        )
        _PIPELINE_MARKET_DATA = loader.load_all(apply_universe_filters=False).sort_index()
        _PIPELINE_CALENDAR = loader.trading_calendar
        _PIPELINE_CONSTITUENTS = loader.constituents
        _PIPELINE_DATES = pd.DatetimeIndex(
            _PIPELINE_MARKET_DATA.index.get_level_values("date").unique()
        ).sort_values()
        _PIPELINE_SYMBOLS = sorted(
            str(value) for value in _PIPELINE_MARKET_DATA.index.get_level_values("symbol").unique()
        )

        base_names = sorted(_PIPELINE_BASE_CONFIGS)
        # 机器学习动量因子的年度扩展训练依赖完整输出路径；增量运行时仍从
        # 正式起点重建该单因子，再由后续矩阵阶段只截取请求区间。
        base_tasks = [] if expansion_only else [
            (
                name,
                _PIPELINE_BASE_CONFIGS[name],
                (
                    min(pd.Timestamp(start), pd.Timestamp(DEFAULT_START_DATE))
                    .strftime("%Y-%m-%d")
                    if name == "momentum_ml_252n20d"
                    else start
                ),
                end,
                str(_PIPELINE_OUTPUT_ROOT),
            )
            for name in base_names
        ]
        print(f"BASE_VALUES_START factors={len(base_tasks)} workers={workers}", flush=True)
        if base_tasks:
            _run_parallel(_calculate_base_values, base_tasks, workers, "基础因子值")
        print(f"BASE_VALUES_DONE factors={len(base_names)} reports=0", flush=True)

        if not expansion_only:
            print(f"BASE_FILL_START factors={len(base_names)} workers={workers}", flush=True)
            _run_parallel(_fill_factor_values, base_names, workers, "基础因子缺失值回填")
            print(f"BASE_FILL_DONE factors={len(base_names)}", flush=True)

        matrix_names = sorted({
            name for derived_name in derived_names
            for name in _PIPELINE_CONFIGS[derived_name]["params"]["input_factors"]
        })
        print(f"BASE_MATRIX_START factors={len(matrix_names)} workers={workers}", flush=True)
        _run_parallel(_build_base_matrix, matrix_names, workers, "基础因子矩阵")
        print("BASE_MATRIX_DONE", flush=True)

        derived_tasks = derived_names
        print(f"DERIVED_VALUES_START factors={len(derived_tasks)} workers={workers}", flush=True)
        if derived_tasks:
            _run_parallel(_calculate_derived_values, derived_tasks, workers, "派生因子值")
        print(f"DERIVED_VALUES_DONE factors={len(derived_names)} reports=0", flush=True)
        shutil.rmtree(_PIPELINE_WORK_DIR / "base_matrices", ignore_errors=True)
        print("BASE_MATRIX_CLEANED", flush=True)

        print(f"DERIVED_FILL_START factors={len(derived_names)} workers={workers}", flush=True)
        _run_parallel(
            _fill_factor_values,
            derived_names,
            workers,
            "派生因子缺失值回填",
        )
        print(f"DERIVED_FILL_DONE factors={len(derived_names)}", flush=True)

        report_names = derived_names if expansion_only else sorted(_PIPELINE_CONFIGS)
        _run_report_stages(report_names,workers,execution_prices=execution_prices,
                           benchmark=return_benchmark,security_status=security_status)
    finally:
        if _PIPELINE_WORK_DIR is not None:
            shutil.rmtree(_PIPELINE_WORK_DIR, ignore_errors=True)
        if RUNTIME_ROOT.is_dir() and not any(RUNTIME_ROOT.iterdir()):
            RUNTIME_ROOT.rmdir()


# 因子流水线共享的逐日成分股来源；收益计算由return_engine.py完成。
WEEKLY_CONSTITUENTS = PROJECT_ROOT / "data/zz500/zz500_daily_constituent_stock.parquet"


def _load_return_engine():
    return importlib.import_module("return_engine")


# 分钟因子复用统一的IC、收益和报告阶段，每次重新计算所选因子。
_MINUTE_SHARED = (None, None)


def run_minute_pipeline(argv=None):
    global _MINUTE_SHARED
    global _PIPELINE_CONFIGS, _PIPELINE_MARKET_DATA, _PIPELINE_CALENDAR
    global _PIPELINE_CONSTITUENTS, _PIPELINE_DATES, _PIPELINE_SYMBOLS, _PIPELINE_OUTPUT_ROOT
    global _PIPELINE_IC_OUTPUT_ROOT, _PIPELINE_RETURN_OUTPUT_ROOT
    engine = _load_return_engine()
    parser = argparse.ArgumentParser(
        prog='run.py --minute-pipeline',
        description='重新计算分钟因子值、每日Rank IC、自然周收益及MD/HTML报告。')
    parser.add_argument('--start', default='2020-01-02')
    parser.add_argument('--end', default='2026-06-30')
    parser.add_argument('--factor', action='append')
    parser.add_argument('--value-root', type=resolve_project_path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--ic-root', type=resolve_project_path, default=DEFAULT_IC_OUTPUT_ROOT)
    parser.add_argument('--return-root', type=resolve_project_path, default=PROJECT_ROOT / 'outputs/zz500/factor_return')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args(argv)
    if args.workers < 1:
        parser.error('--workers必须为正整数')
    if pd.Timestamp(args.start) >= pd.Timestamp(args.end):
        parser.error('--start必须早于--end')
    args.value_root, args.ic_root, args.return_root = (
        p.resolve() for p in (args.value_root, args.ic_root, args.return_root))
    roots = (args.value_root, args.ic_root, args.return_root)
    if any(a == b or a in b.parents or b in a.parents
           for i, a in enumerate(roots) for b in roots[i + 1:]):
        parser.error('三个输出根目录必须独立且互不包含')
    validate_shared_factor_ids()
    configs = json.loads((PROJECT_ROOT / 'config/factor_configs_minute_base.json').read_text())
    for config in configs.values():
        config['description'] = FactorRegistry.get(config['relay_class']).description
    if args.factor:
        unknown = set(args.factor).difference(configs)
        if unknown:
            parser.error(f'未知分钟因子: {sorted(unknown)}')
        configs = {name: config for name, config in configs.items() if name in args.factor}
    required = [DEFAULT_DATA_DIR, DEFAULT_MINUTE_DATA_DIR, WEEKLY_CONSTITUENTS,
                DEFAULT_SECURITY_STATUS_PATH, engine.DEFAULT_EXECUTION_PRICES,
                engine.DEFAULT_BENCHMARK]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f'缺少既有回测输入: {missing}')
    print(json.dumps(portable_payload(dict(
        factors=len(configs), workers=args.workers, start=args.start, end=args.end,
        value_root=args.value_root, ic_root=args.ic_root, return_root=args.return_root)),
        ensure_ascii=False, indent=2), flush=True)
    if args.plan_only:
        return
    args.value_root.mkdir(parents=True, exist_ok=True)
    with (args.value_root / '.minute_three_outputs.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # 合并全部所选因子的日线输入；同名异源不能静默覆盖。
        sources = runtime_inputs('zz500', constituents=WEEKLY_CONSTITUENTS)
        warmup = 0
        for name, config in configs.items():
            factor = FactorRegistry.get(config['relay_class'])(**config.get('params', {}))
            warmup = max(warmup, getattr(factor, 'warmup_days', 0), factor.minute_window_days - 1)
            for logical, source in getattr(factor, 'INPUTS', {}).items():
                if logical in sources and sources[logical] != source:
                    raise ValueError(f'分钟共享日线输入冲突: {name}: {logical}')
                sources[logical] = source
        loader = FactorDataLoader(runtime_inputs=sources, universe='zz500',
                                  start=args.start, end=args.end, warmup_days=warmup,
                                  context_only=True)
        daily = loader.load_all(apply_universe_filters=False)
        _MINUTE_SHARED = (loader, daily)
        print(f'MINUTE_VALUES_START factors={len(configs)} workers={args.workers}', flush=True)
        if args.workers == 1:
            _run_minute_batch(args, configs)
        else:
            failures = []
            with ProcessPoolExecutor(max_workers=min(args.workers, len(configs)),
                                     mp_context=mp.get_context('fork')) as pool:
                futures = {pool.submit(_run_minute_batch, args, {name: config}): name
                           for name, config in configs.items()}
                for completed, future in enumerate(as_completed(futures), start=1):
                    name = futures[future]
                    try:
                        future.result()
                        print(f'PROGRESS completed={completed}/{len(configs)} factor={name}', flush=True)
                    except Exception:
                        failures.append(name)
                        print(f'WORKER_FAILED {name}\n{traceback.format_exc()}', flush=True)
            if failures:
                raise RuntimeError(f'失败因子: {failures}')
        _PIPELINE_CONFIGS = configs
        _PIPELINE_MARKET_DATA = daily
        _PIPELINE_CALENDAR, _PIPELINE_CONSTITUENTS = loader.trading_calendar, loader.constituents
        _PIPELINE_DATES = pd.DatetimeIndex(daily.index.get_level_values('date').unique()).sort_values()
        _PIPELINE_SYMBOLS = sorted(daily.index.get_level_values('symbol').unique())
        _PIPELINE_OUTPUT_ROOT, _PIPELINE_IC_OUTPUT_ROOT = args.value_root, args.ic_root
        _PIPELINE_RETURN_OUTPUT_ROOT = args.return_root
        _run_report_stages(list(configs), args.workers)
        print(f'ALL_COMPLETED factors={len(configs)}', flush=True)


def _run_minute_batch(args, configs):
    """计算所选分钟因子值，全体完成后再统一计算IC、收益和报告。"""
    shared_loader, daily = _MINUTE_SHARED
    failures = []
    for name, config in configs.items():
        try:
            runner = Runner(
                factor_name=name, relay_class=config['relay_class'],
                factor_params=config['params'], factor_config=config,
                start=args.start, end=args.end, data_dir=DEFAULT_DATA_DIR,
                constituents_path=WEEKLY_CONSTITUENTS,
                output_dir=args.value_root / name, forward_periods=(5,))
            runner.data_loader, runner.data = shared_loader, daily
            runner.calculate(save=True)
        except Exception:
            failures.append(name)
            print(f'FAILED {name}\n{traceback.format_exc()}', flush=True)
    if failures:
        raise RuntimeError(f'分钟因子值失败: {failures}')
    return len(configs)


def select_single_factors(configs: dict, *, factor=None, prefix=None) -> dict:
    """从原配置按确切名称及前缀取交集，不创建配置副本文件。"""
    if factor is not None and factor not in configs:
        raise ValueError(f'配置中不存在因子: {factor}')
    selected = {name: config for name, config in configs.items()
                if (factor is None or name == factor)
                and (prefix is None or name.startswith(prefix))}
    if not selected:
        raise ValueError(f'没有匹配的因子: factor={factor!r}, prefix={prefix!r}')
    if any(config.get('params', {}).get('expansion_kind') for config in selected.values()):
        raise ValueError('派生因子必须通过 --pipeline 运行，不能按普通注册因子执行')
    return selected


def _run_single_factor(task):
    """一个任务独立完成因子值、每日IC、自然周收益及报告。"""
    name, original, settings = task
    try:
        config = {**original, 'params': dict(original.get('params', {}))}
        if name == 'momentum_ml_252n20d':
            config['params']['universe'] = settings['universe']
        importlib.import_module(config['module'])
        runner = Runner(
            factor_name=name, relay_class=config['relay_class'],
            factor_params=config['params'], factor_config=config,
            start=settings['start'], end=settings['end'],
            data_dir=settings['data_dir'], constituents_path=settings['constituents'],
            output_dir=settings['output_root'] / name,
            is_financial_factor=name in settings['financial_factors'],
            universe_name=str(UNIVERSE_SETTINGS[settings['universe']]['name']),
            security_status_path=settings['security_status'],
        )
        runner.ic_output_dir = settings['ic_output_root'] / name
        runner.return_output_dir = settings['return_output_root'] / name
        runner.execution_prices = settings['execution_prices']
        runner.return_benchmark = settings['return_benchmark']
        runner.run()
        return _pipeline_result(name, 'completed')
    except Exception:
        return _pipeline_result(name, 'failed', traceback=traceback.format_exc())


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    modes = [flag for flag in ("--minute-pipeline", "--pipeline") if flag in argv]
    if len(modes) > 1 or (modes and any(a == '--mode' or a.startswith('--mode=') for a in argv)):
        raise ValueError("运行模式互斥，请只选择一个流程入口")
    if "--minute-pipeline" in argv:
        argv.remove("--minute-pipeline")
        return run_minute_pipeline(argv)
    parser = argparse.ArgumentParser(description="批量计算并评估配置文件中的因子。")
    parser.add_argument('--mode', choices=('single',), default=None,
                        help='single：每个因子独立运行值、IC、收益和报告，支持--workers并行。')
    parser.add_argument('--factor-prefix', default=None,
                        help='single模式仅选择名称以该前缀开头的因子，例如chip_high_anchor_。')
    parser.add_argument('--plan-only', action='store_true',
                        help='single模式只显示选中数量、并行数和区间，不运行计算。')
    parser.add_argument(
        "--minute-pipeline", action="store_true",
        help="分钟因子值、每日 Rank IC、周收益流水线；选项见 --minute-pipeline --help。",
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help=(
            "运行正式全流程：基础值→基础回填→矩阵→派生值→派生回填"
            "→每日IC→精细自然周收益→MD及HTML。"
        ),
    )
    parser.add_argument(
        "--factor-config",
        type=resolve_project_path,
        default=DEFAULT_BASE_FACTOR_CONFIG,
        help=(
            "基础日频配置；单独运行与正式 --pipeline 均读取该文件。"
        ),
    )
    parser.add_argument(
        "--factor",
        default=None,
        help="只运行配置中的指定因子；未指定时运行配置内全部因子。",
    )
    parser.add_argument(
        "--start",
        default=DEFAULT_START_DATE,
        help=f"因子计算和回测起始日，默认使用 {DEFAULT_START_DATE}。",
    )
    parser.add_argument(
        "--end",
        default="2026-06-30",
        help="因子计算和回测截止日；默认使用已确认的2026-06-30；不纳入此后的数据。",
    )
    parser.add_argument(
        "--universe",
        choices=tuple(UNIVERSE_SETTINGS),
        default="zz500",
        help="股票池：zz500=中证500，zz1000=中证1000；默认zz500。",
    )
    parser.add_argument(
        "--data-dir",
        type=resolve_project_path,
        default=None,
        help="公共日频行情分区目录；公式输入仍由各因子 INPUTS 声明。",
    )
    parser.add_argument(
        "--constituent-index",
        default=None,
        help="指数代码；zz500默认000905.SH，zz1000默认000852.SH。",
    )
    parser.add_argument(
        "--financial-factor-config",
        type=resolve_project_path,
        default=DEFAULT_FINANCIAL_FACTOR_CONFIG,
        help=(
            "财务类因子名单配置；默认使用 "
            "config/financial_factors.json。"
        ),
    )
    parser.add_argument(
        "--output-root",
        type=resolve_project_path,
        default=None,
        help="单因子输出根目录；默认使用 outputs/<universe>/factor_value。",
    )
    parser.add_argument(
        "--ic-output-root",
        type=resolve_project_path,
        default=None,
        help="全量因子逐日IC输出根目录；默认使用 outputs/<universe>/factor_ic。",
    )
    parser.add_argument("--return-output-root",type=resolve_project_path,default=None,
        help="精细自然周收益输出根目录；默认outputs/<universe>/factor_return。")
    parser.add_argument("--execution-prices",type=resolve_project_path,
        default=DEFAULT_STOCK_DAY_PATH)
    parser.add_argument("--return-benchmark",type=resolve_project_path,
        default=DEFAULT_INDEX_PATH)
    parser.add_argument("--security-status",type=resolve_project_path,default=DEFAULT_SECURITY_STATUS_PATH)
    parser.add_argument(
        "--expansion-factor-config",
        type=resolve_project_path,
        default=DEFAULT_EXPANSION_FACTOR_CONFIG,
        help="只包含组合扩展因子的配置；基础因子从 --factor-config 读取。",
    )
    parser.add_argument('--expansion-only', action='store_true',
                        help='全流程仅计算扩展因子，严格复用基础值且不改写基础输出。')
    parser.add_argument('--expansion-start', type=int, default=1,
                        help='扩展专用流程起始编号（含），默认1。')
    parser.add_argument(
        "--workers", type=int, default=120, help="single模式或全流程并行进程数，默认120。"
    )
    parser.add_argument(
        "--fill-seed-root",
        type=resolve_project_path,
        default=None,
        help=(
            "增量隔离计算时，从该既有因子目录读取起始日前最后值，"
            "保证跨边界前向回填口径一致。"
        ),
    )
    args = parser.parse_args(argv)
    if args.workers < 1:
        parser.error('--workers必须为正整数')
    if (args.factor_prefix is not None or args.plan_only) and args.mode != 'single':
        parser.error('--factor-prefix和--plan-only必须与--mode single一起使用')
    if args.mode == 'single' and pd.Timestamp(args.start) >= pd.Timestamp(args.end):
        parser.error('--start必须早于--end')
    if args.expansion_start < 1 or args.expansion_start > 99999:
        parser.error('--expansion-start 必须在1至99999之间')
    if (args.expansion_only or args.expansion_start != 1) and not args.pipeline:
        parser.error('--expansion-only/--expansion-start 必须与 --pipeline 一起使用')
    if args.expansion_start != 1 and not args.expansion_only:
        parser.error('--expansion-start 必须与 --expansion-only 一起使用')

    universe_settings = UNIVERSE_SETTINGS[args.universe]
    data_dir = (
        args.data_dir
        if args.data_dir is not None
        else PROJECT_ROOT / "data" / args.universe / "stock_day"
    )
    constituent_index = args.constituent_index or str(universe_settings["index"])
    output_root = args.output_root or PROJECT_ROOT / "outputs" / args.universe / "factor_value"
    ic_output_root = args.ic_output_root or PROJECT_ROOT / "outputs" / args.universe / "factor_ic"

    if args.pipeline:
        run_full_pipeline(
            expansion_config_path=args.expansion_factor_config,
            base_config_path=args.factor_config,
            output_root=output_root,
            ic_output_root=ic_output_root,
            data_dir=data_dir,

            constituent_index=constituent_index,
            universe=args.universe,
            start=args.start,
            end=args.end,
            workers=args.workers,
            fill_seed_root=args.fill_seed_root,
            return_output_root=args.return_output_root,
            execution_prices=args.execution_prices,
            return_benchmark=args.return_benchmark,
            security_status=args.security_status,
            expansion_only=args.expansion_only,
            expansion_start=args.expansion_start,
        )
        raise SystemExit(0)

    factor_config_path = args.factor_config
    with factor_config_path.open("r", encoding="utf-8") as f:
        factor_configs = json.load(f)
    validate_shared_factor_ids()
    validate_factor_ids(factor_configs)
    try:
        factor_configs = select_single_factors(factor_configs, factor=args.factor,
                                               prefix=args.factor_prefix)
    except ValueError as exc:
        parser.error(str(exc))
    with args.financial_factor_config.open("r", encoding="utf-8") as f:
        financial_factor_config = json.load(f)
    financial_factor_names = set(financial_factor_config["factor_names"])

    settings = dict(
        universe=args.universe, start=args.start, end=args.end, data_dir=data_dir,
        constituents=(WEEKLY_CONSTITUENTS if args.universe == 'zz500' else data_dir / 'constituents_daily.parquet'),
        output_root=output_root, ic_output_root=ic_output_root,
        return_output_root=args.return_output_root or output_root.parent / 'factor_return',
        financial_factors=financial_factor_names, security_status=args.security_status,
        execution_prices=args.execution_prices, return_benchmark=args.return_benchmark,
    )
    tasks = [(name, config, settings) for name, config in factor_configs.items()]
    if args.mode == 'single':
        workers = min(args.workers, len(tasks))
        print(f'SINGLE_START factors={len(tasks)} workers={workers} '
              f'start={args.start} end={args.end} factor_prefix={args.factor_prefix!r}', flush=True)
        if args.plan_only:
            print('PLAN_ONLY no_computation=True', flush=True)
            return
        for name, config in factor_configs.items():
            validate_report_config(name, config)
        if workers > 1:
            _run_parallel(_run_single_factor, tasks, workers, 'single模式完整回测')
        else:
            for task in tqdm(tasks, total=len(tasks), desc='single模式完整回测', unit='factor'):
                result = _run_single_factor(task)
                if result['status'] == 'failed':
                    raise RuntimeError(result['traceback'])
        print(f'SINGLE_DONE completed={len(tasks)}', flush=True)
        return
    for task in tqdm(tasks, total=len(tasks), desc='自主因子回测', unit='factor'):
        result = _run_single_factor(task)
        if result['status'] == 'failed':
            raise RuntimeError(result['traceback'])


if __name__ == "__main__":
    main()
