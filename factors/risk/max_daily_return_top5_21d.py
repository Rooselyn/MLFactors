"""max_daily_return_top5_21d：风险；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
import numpy as np
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
}


@register_factor
@fixed_factor('max_daily_return_top5_21d', {'top_n': 5, 'min_obs': None, 'lookback': 21, 'rebalance_step': 1})
class Factor_max_daily_return_top5_21d(BaseFactor):
    """过去 21 日前 5 大单日收益均值，值越高表示博彩型极端上涨特征越强。"""
    INPUTS = INPUTS

    name = 'max_daily_return_top5_21d'
    description = "海通15博彩型因子：过去21日前5大单日收益均值"

    def __init__(
        self,
        top_n: int = 5,
        min_obs: int | None = None,
        lookback: int = 21,
        rebalance_step: int = 1,
    ) -> None:
        self.top_n = top_n
        self.min_obs = min_obs
        self.lookback = lookback
        # 保留参数以兼容旧调用；当前版本每天滚动计算，不再按该参数抽样。
        self.rebalance_step = rebalance_step

    @staticmethod
    def _top_n_mean(values: np.ndarray, top_n: int, min_obs: int) -> float:
        """计算 rolling.apply 传入窗口里的前 top_n 大日收益均值。"""
        clean = values[np.isfinite(values)]
        if len(clean) < min_obs:
            return np.nan
        top_count = min(top_n, len(clean))
        return float(np.partition(clean, -top_count)[-top_count:].mean())

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        if 'close_hfq' not in data.columns:
            raise ValueError("字段 close_hfq 缺失")
        if not isinstance(data.index, pd.MultiIndex) or data.index.names[:2] != ["date", "symbol"]:
            raise ValueError("因子输入必须使用 (date, symbol) MultiIndex")

        min_obs = self.top_n if self.min_obs is None else self.min_obs
        if self.top_n <= 0:
            raise ValueError("top_n 必须为正整数")
        if min_obs <= 0:
            raise ValueError("min_obs 必须为正整数")
        if self.lookback <= 0:
            raise ValueError("lookback 必须为正整数")

        close = data['close_hfq'].unstack("symbol").astype(float).sort_index()
        returns = close.pct_change(fill_method=None)
        factor = returns.rolling(window=self.lookback, min_periods=min_obs).apply(
            lambda values: self._top_n_mean(values, top_n=self.top_n, min_obs=min_obs),
            raw=True,
        )
        factor.iloc[: self.lookback] = np.nan

        if constituents:
            constituent_mask = pd.DataFrame(
                [
                    [symbol in constituents.get(str(date.date()), set()) for symbol in close.columns]
                    for date in close.index
                ],
                index=close.index,
                columns=close.columns,
            )
            factor = factor.where(constituent_mask)

        factor.index.name = "date"
        factor.columns.name = "symbol"
        return factor
