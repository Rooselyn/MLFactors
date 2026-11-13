"""Open Source Asset Pricing（Chen–Zimmermann）

公式：r_m=C_{月m末}/C_{月m−1末}−1；原目录：STreversal（Short term reversal）；追踪：PF01661；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'osap_monthly_reversal_1m', 'engine': 'market'}

@register_factor
@fixed_factor('osap_monthly_reversal_1m', {})
class Factor_osap_monthly_reversal_1m(PublicFactor):
    name = 'osap_monthly_reversal_1m'
    description = 'r_m=C_{月m末}/C_{月m−1末}−1；原目录：STreversal（Short term reversal）；追踪：PF01661；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。'
    INPUTS = INPUTS
    SPEC = SPEC
