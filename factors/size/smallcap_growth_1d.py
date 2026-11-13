"""smallcap_growth_1d：规模；输入来源由本文件维护。"""
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
    'total_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "total_mv"),
}


@register_factor
@fixed_factor('smallcap_growth_1d', {'lower': 0.01, 'upper': 0.99, 'use_rank': False})
class Factor_smallcap_growth_1d(BaseFactor):
    """海通83小市值成长弹性近似因子：市值越小，因子值越高。"""
    INPUTS = INPUTS

    name = 'smallcap_growth_1d'
    description = "小市值成长弹性因子：-log(total_mv) 横截面标准化"

    def __init__(
        self,
        lower: float = 0.01,
        upper: float = 0.99,
        use_rank: bool = False,
    ) -> None:
        self.lower = lower
        self.upper = upper
        self.use_rank = use_rank

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        if 'total_mv' not in data.columns:
            raise ValueError("字段 total_mv 缺失")
        if not isinstance(data.index, pd.MultiIndex) or data.index.names[:2] != ["date", "symbol"]:
            raise ValueError("因子输入必须使用 (date, symbol) MultiIndex")

        total_mv = data['total_mv'].unstack("symbol").astype(float).sort_index()
        total_mv.index.name = "date"
        total_mv.columns.name = "symbol"
        log_cap = np.log(total_mv.where(total_mv > 0))
        raw_score = -log_cap

        if self.use_rank:
            score = raw_score.rank(axis=1, pct=True, ascending=True)
            score = score.where(raw_score.notna())
        else:
            low = raw_score.quantile(self.lower, axis=1)
            high = raw_score.quantile(self.upper, axis=1)
            winsorized = raw_score.clip(lower=low, upper=high, axis=0)
            mean = winsorized.mean(axis=1)
            std = winsorized.std(axis=1, ddof=0).replace(0, np.nan)
            score = winsorized.sub(mean, axis=0).div(std, axis=0)

        score.index.name = "date"
        score.columns.name = "symbol"
        if not constituents:
            return score

        mask = pd.DataFrame(False, index=score.index, columns=score.columns)
        for date in score.index:
            allowed = constituents.get(str(pd.Timestamp(date).date()), set())
            if allowed:
                present = score.columns.intersection(allowed)
                mask.loc[date, present] = True
        return score.where(mask)
