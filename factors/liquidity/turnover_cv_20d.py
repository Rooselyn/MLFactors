"""turnover_cv_20d：流动性；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
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
@fixed_factor('turnover_cv_20d', {'window': 20, 'min_periods': 15})
class Factor_turnover_cv_20d(BaseFactor):
    """换手率变异系数因子：捕捉交易行为波动对收益的预测能力。

    核心思想：成交量波动大的股票，说明投资者分歧大，不确定性高，
    根据流动性溢价理论，这种股票需要更高的风险补偿，预期收益更低。
    通过计算过去20日换手率的变异系数（标准差/均值）来衡量交易行为波动性。

    Parameters
    ----------
    window : int, default 20
        计算变异系数的时间窗口（交易日），默认20天。
    min_periods : int, default 15
        最少需要的交易日数量，默认15天。
    """
    INPUTS = INPUTS

    name = 'turnover_cv_20d'
    description = "换手率变异系数因子"

    def __init__(self, window: int = 20, min_periods: int = 15) -> None:
        self.window = window
        self.min_periods = min_periods

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

        # 计算滚动变异系数: CV = std / mean
        rolling_mean = turnover.rolling(window=self.window, min_periods=self.min_periods).mean()
        rolling_std = turnover.rolling(window=self.window, min_periods=self.min_periods).std()

        # 变异系数
        cv = rolling_std / rolling_mean

        # 因子值 = CV（CV越大，未来收益越低）
        signals = cv.copy()

        signals.index.name = "date"
        signals.columns.name = "symbol"
        return signals
