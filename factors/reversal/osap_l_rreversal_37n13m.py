"""Open Source Asset Pricing（Chen–Zimmermann）

公式：∏_{k=13…36}(1+r_{m−k})−1；m为当前已完成月；尾缀表示包含m在内37个月收益的块中跳过最新13个月；原目录：LRreversal（Long-run reversal）；追踪：PF01599；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'osap_l_rreversal_37n13m', 'engine': 'market'}

@register_factor
@fixed_factor('osap_l_rreversal_37n13m', {})
class Factor_osap_l_rreversal_37n13m(PublicFactor):
    name = 'osap_l_rreversal_37n13m'
    description = '∏_{k=13…36}(1+r_{m−k})−1；m为当前已完成月；尾缀表示包含m在内37个月收益的块中跳过最新13个月；原目录：LRreversal（Long-run reversal）；追踪：PF01599；[来源](https://github.com/OpenSourceAP/CrossSection/blob/8db892442c2c3a3779b0f1eac4370d3655be15a1/SignalDoc.csv)。'
    INPUTS = INPUTS
    SPEC = SPEC
