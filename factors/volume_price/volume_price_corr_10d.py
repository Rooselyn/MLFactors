"""volume_price_corr_10d：量价；输入来源由本文件维护。"""
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
    'vol': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "vol"),
    'total_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "total_mv"),
}


@register_factor
@fixed_factor('volume_price_corr_10d', {'window': 10})
class Factor_volume_price_corr_10d(BaseFactor):
    """量价相关性因子：捕捉量价背离/同向对收益的预测能力。

    核心思想：放量上涨的股票在存量资金博弈市场中难以持续，
    未来大概率下跌；放量下跌的股票风险已释放，未来表现更好。
    通过计算收盘价与换手率的Pearson相关系数来衡量量价关系。

    Parameters
    ----------
    window : int, default 10
        计算相关系数的时间窗口（交易日），默认10天（半个月）。
    """
    INPUTS = INPUTS

    name = 'volume_price_corr_10d'
    description = "量价相关性因子"

    def __init__(self, window: int = 10) -> None:
        self.window = window

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        close = data['close_hfq'].unstack("symbol").astype(float).sort_index()
        vol = data['vol'].unstack("symbol").astype(float).sort_index()
        total_mv = data['total_mv'].unstack("symbol").astype(float).sort_index()

        # 计算近似换手率: turnover = vol × close_hfq / total_mv
        turnover = vol * close / total_mv

        # 计算滚动相关系数
        signals = pd.DataFrame(np.nan, index=close.index, columns=close.columns)

        for symbol in close.columns:
            close_col = close[symbol]
            turnover_col = turnover[symbol]

            # 滚动计算Pearson相关系数
            corr = close_col.rolling(window=self.window).corr(turnover_col)
            signals[symbol] = corr

        signals.index.name = "date"
        signals.columns.name = "symbol"
        return signals
