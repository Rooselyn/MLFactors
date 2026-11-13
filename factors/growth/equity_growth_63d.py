"""equity_growth_63d：成长；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
    'total_hldr_eqy_exc_min_int': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_hldr_eqy_exc_min_int", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'industry_sw_1': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "industry_sw_1"),
}


@register_factor
@fixed_factor('equity_growth_63d', {})
class Factor_equity_growth_63d(BaseFactor):
    """Shareholder equity growth over 63 trading days."""
    INPUTS = INPUTS

    name = 'equity_growth_63d'
    description = "Shareholder equity growth over 63 trading days."

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        equity = data['total_hldr_eqy_exc_min_int']
        equity_prev = equity.groupby(level="symbol").shift(63)
        factor = (equity - equity_prev) / equity_prev.abs().replace(0, pd.NA)

        result = factor.unstack(level="symbol")
        result.index.name = "date"
        result.columns.name = "symbol"
        return result
