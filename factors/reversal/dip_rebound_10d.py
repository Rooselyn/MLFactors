"""dip_rebound_10d：反转；输入来源由本文件维护。"""
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
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "low_hfq"),
}


@register_factor
@fixed_factor('dip_rebound_10d', {'window': 10, 'min_periods': 5, 'shift_days': 0})
class Factor_dip_rebound_10d(BaseFactor):
    """过去 10 日从日内最低价到收盘价的平均回升幅度。"""
    INPUTS = INPUTS

    name = 'dip_rebound_10d'
    description = "海通18价格形态因子：10日平均 log(close/low)"

    def __init__(
        self,
        window: int = 10,
        min_periods: int = 5,
        shift_days: int = 0,
    ) -> None:
        self.window = window
        self.min_periods = min_periods
        self.shift_days = shift_days

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        """计算最近 window 个交易日 log(close / low) 的均值。"""
        if 'low_hfq' not in data.columns:
            raise ValueError("字段 adj_low 缺失")
        if not isinstance(data.index, pd.MultiIndex) or data.index.names[:2] != ["date", "symbol"]:
            raise ValueError("因子输入必须使用 (date, symbol) MultiIndex")
        if 'close_hfq' not in data.columns:
            raise ValueError("字段 close_hfq 缺失")

        low = data['low_hfq'].unstack("symbol").astype(float).sort_index()
        close = data['close_hfq'].unstack("symbol").astype(float).sort_index()
        close = close.reindex(index=low.index, columns=low.columns)
        valid = (low > 0) & (close > 0) & (close >= low)
        daily_value = np.log(close.where(valid) / low.where(valid))
        factor = daily_value.rolling(
            window=self.window,
            min_periods=self.min_periods,
        ).mean()
        if self.shift_days:
            factor = factor.shift(self.shift_days)

        factor.index.name = "date"
        factor.columns.name = "symbol"
        if not constituents:
            return factor

        mask = pd.DataFrame(False, index=factor.index, columns=factor.columns)
        for date in factor.index:
            allowed = constituents.get(str(pd.Timestamp(date).date()), set())
            if allowed:
                present = factor.columns.intersection(allowed)
                mask.loc[date, present] = True
        return factor.where(mask)
