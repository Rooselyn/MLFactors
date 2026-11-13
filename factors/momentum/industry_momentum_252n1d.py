"""industry_momentum_252n1d：动量；输入来源由本文件维护。"""
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
    'industry_sw_1': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "industry_sw_1"),
}


@register_factor
@fixed_factor('industry_momentum_252n1d', {'lookback': 252, 'exclude_recent': 1})
class Factor_industry_momentum_252n1d(BaseFactor):
    INPUTS = INPUTS
    name = 'industry_momentum_252n1d'
    description = "申万一级行业动量因子（剔除自身的同行业平均收益）"

    def __init__(
        self,
        period: int = 1,
        lookback: int | None = None,
        exclude_recent: int | None = None,
    ) -> None:
        self.period = period
        self.lookback = lookback
        self.exclude_recent = exclude_recent
        if (lookback is None) != (exclude_recent is None):
            raise ValueError("lookback和exclude_recent必须同时提供")
        if lookback is not None:
            if not isinstance(lookback, int) or not isinstance(exclude_recent, int):
                raise TypeError("lookback和exclude_recent必须是整数")
            if not 0 < exclude_recent < lookback:
                raise ValueError("exclude_recent必须是小于lookback的正整数")
            self.factor_name = self.name
        else:
            self.factor_name = self.name

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        close = data['close_hfq'].unstack("symbol").astype(float).sort_index()
        industry = data['industry_sw_1'].unstack("symbol")

        if self.lookback is None:
            returns = close.pct_change(self.period, fill_method=None)
        else:
            # 在每个信号日仅使用 t-lookback 至 t-exclude_recent 的收益，
            # 排除近期可能存在的短期反转，再计算剔除自身的同行业均值。
            returns = close.shift(self.exclude_recent) / close.shift(self.lookback) - 1
        returns = returns.replace([np.inf, -np.inf], np.nan)

        # 展平为长表以进行高效的 Groupby 运算
        df = pd.DataFrame(
            {"ret": returns.stack(), 'industry': industry.stack()}
        ).dropna(subset=['industry'])

        # 计算每个行业在每一天的总收益和股票数量
        grp = df.groupby(["date", 'industry'])["ret"]
        df["grp_sum"] = grp.transform("sum")
        df["grp_count"] = grp.transform("count")

        # 自身收益缺失时未计入有效样本数，不能再减1；零价格产生的无穷收益不参与均值。
        peer_count = df["grp_count"] - df["ret"].notna().astype(int)
        df["peer_mean"] = (df["grp_sum"] - df["ret"].fillna(0)) / (
            peer_count.where(peer_count > 0)
        )

        return df["peer_mean"].unstack("symbol")
