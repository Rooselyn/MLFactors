"""Open Source Asset Pricing（Chen–Zimmermann）

公式：log(close)，仅close>0；原目录：Price（Price）；追踪：PF01632；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close'),
}
SPEC = {'name': 'osap_log_price_1d', 'engine': 'market'}

@register_factor
@fixed_factor('osap_log_price_1d', {})
class Factor_osap_log_price_1d(PublicFactor):
    name = 'osap_log_price_1d'
    description = 'log(close)，仅close>0；原目录：Price（Price）；追踪：PF01632；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。'
    INPUTS = INPUTS
    SPEC = SPEC
