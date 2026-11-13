"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：G=(TTM(revenue)−TTM(oper_cost))/TTM(revenue)；每日截面rank(G)；原目录：gpm_ttm；追踪：PF02591；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'oper_cost': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'oper_cost', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'tushare_gross_margin_rank_pit_4q', 'engine': 'financial', 'expression': '(v0-v1)/v0', 'leaves': {'v0': ['financial_income', 'revenue', 'T', 0], 'v1': ['financial_income', 'oper_cost', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': True}

@register_factor
@fixed_factor('tushare_gross_margin_rank_pit_4q', {})
class Factor_tushare_gross_margin_rank_pit_4q(PublicFactor):
    name = 'tushare_gross_margin_rank_pit_4q'
    description = 'G=(TTM(revenue)−TTM(oper_cost))/TTM(revenue)；每日截面rank(G)；原目录：gpm_ttm；追踪：PF02591；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
