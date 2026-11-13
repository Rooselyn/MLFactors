"""Open Source Asset Pricing（Chen–Zimmermann）

公式：(revt_y−cogs_y)/at_y；符号物理映射：revt=total_revenue, cogs=oper_cost, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：GP（gross profits / total assets）；追踪：PF01575；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'total_revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'oper_cost': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'oper_cost', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'osap_gross_profit_assets_pit_1y', 'engine': 'financial', 'expression': '(v0-v1)/v2', 'leaves': {'v0': ['financial_income', 'total_revenue', 'Y', 0], 'v1': ['financial_income', 'oper_cost', 'Y', 0], 'v2': ['financial_balance_sheet', 'total_assets', 'Y', 0]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('osap_gross_profit_assets_pit_1y', {})
class Factor_osap_gross_profit_assets_pit_1y(PublicFactor):
    name = 'osap_gross_profit_assets_pit_1y'
    description = '(revt_y−cogs_y)/at_y；符号物理映射：revt=total_revenue, cogs=oper_cost, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：GP（gross profits / total assets）；追踪：PF01575；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。'
    INPUTS = INPUTS
    SPEC = SPEC
