"""Open Source Asset Pricing（Chen–Zimmermann）

公式：(xrd_y+0.8xrd_{y−1}+0.6xrd_{y−2}+0.4xrd_{y−3}+0.2xrd_{y−4})/at_y；符号物理映射：xrd=rd_exp, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：RDcap（R&D capital-to-assets）；追踪：PF01637；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。；同定义来源别名：JKP Global Factor Data（Jensen–Kelly–Pedersen）:rd5_at（R&D capital-to-book assets）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'rd_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'rd_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'osap_rd_capital_assets_pit_5y', 'engine': 'financial', 'expression': '(v0+0.8*v1+0.6*v2+0.4*v3+0.2*v4)/v5', 'leaves': {'v0': ['financial_income', 'rd_exp', 'Y', 0], 'v1': ['financial_income', 'rd_exp', 'Y', 4], 'v2': ['financial_income', 'rd_exp', 'Y', 8], 'v3': ['financial_income', 'rd_exp', 'Y', 12], 'v4': ['financial_income', 'rd_exp', 'Y', 16], 'v5': ['financial_balance_sheet', 'total_assets', 'Y', 0]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('osap_rd_capital_assets_pit_5y', {})
class Factor_osap_rd_capital_assets_pit_5y(PublicFactor):
    name = 'osap_rd_capital_assets_pit_5y'
    description = '(xrd_y+0.8xrd_{y−1}+0.6xrd_{y−2}+0.4xrd_{y−3}+0.2xrd_{y−4})/at_y；符号物理映射：xrd=rd_exp, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：RDcap（R&D capital-to-assets）；追踪：PF01637；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。；同定义来源别名：JKP Global Factor Data（Jensen–Kelly–Pedersen）:rd5_at（R&D capital-to-book assets）'
    INPUTS = INPUTS
    SPEC = SPEC
