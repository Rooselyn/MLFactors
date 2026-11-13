"""GKX94／Green–Hand–Zhang股票特征

公式：((sale_y−cogs_y)/(sale_{y−1}−cogs_{y−1})−1)−(sale_y/sale_{y−1}−1)；符号物理映射：sale=revenue, cogs=oper_cost；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：pchgm_pchsale；追踪：PF01927；[来源](https://dachxiu.chicagobooth.edu/download/ML_supp.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'oper_cost': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'oper_cost', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'gkx_gross_margin_growth_minus_sales_growth_pit_1y', 'engine': 'financial', 'expression': '((v0-v1)/(v2-v3)-1)-(v0/v2-1)', 'leaves': {'v0': ['financial_income', 'revenue', 'Y', 0], 'v1': ['financial_income', 'oper_cost', 'Y', 0], 'v2': ['financial_income', 'revenue', 'Y', 4], 'v3': ['financial_income', 'oper_cost', 'Y', 4]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('gkx_gross_margin_growth_minus_sales_growth_pit_1y', {})
class Factor_gkx_gross_margin_growth_minus_sales_growth_pit_1y(PublicFactor):
    name = 'gkx_gross_margin_growth_minus_sales_growth_pit_1y'
    description = '((sale_y−cogs_y)/(sale_{y−1}−cogs_{y−1})−1)−(sale_y/sale_{y−1}−1)；符号物理映射：sale=revenue, cogs=oper_cost；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：pchgm_pchsale；追踪：PF01927；[来源](https://dachxiu.chicagobooth.edu/download/ML_supp.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
