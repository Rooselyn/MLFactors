"""Open Source Asset Pricing（Chen–Zimmermann）

公式：sale_y/MC_t；符号物理映射：sale=revenue；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：SP（Sales-to-price）；追踪：PF01710；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。；同定义来源别名：JKP Global Factor Data（Jensen–Kelly–Pedersen）:sale_me（Sales-to-market）、PyAnomaly:FUNDA.sale_me
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'),
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'osap_sales_to_market_pit_1y', 'engine': 'financial', 'expression': 'v0/MC', 'leaves': {'v0': ['financial_income', 'revenue', 'Y', 0]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('osap_sales_to_market_pit_1y', {})
class Factor_osap_sales_to_market_pit_1y(PublicFactor):
    name = 'osap_sales_to_market_pit_1y'
    description = 'sale_y/MC_t；符号物理映射：sale=revenue；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：SP（Sales-to-price）；追踪：PF01710；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。；同定义来源别名：JKP Global Factor Data（Jensen–Kelly–Pedersen）:sale_me（Sales-to-market）、PyAnomaly:FUNDA.sale_me'
    INPUTS = INPUTS
    SPEC = SPEC
