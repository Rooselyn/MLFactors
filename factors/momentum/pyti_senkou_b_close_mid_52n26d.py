"""PyTI

公式：lag((max(C,52)+min(C,52))/2,26)；原目录：ichimoku_cloud.senkou_b（period=52）；追踪：PF01431；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_senkou_b_close_mid_52n26d', 'engine': 'explicit', 'period': 14}

@register_factor
@fixed_factor('pyti_senkou_b_close_mid_52n26d', {})
class Factor_pyti_senkou_b_close_mid_52n26d(PublicFactor):
    name = 'pyti_senkou_b_close_mid_52n26d'
    description = 'lag((max(C,52)+min(C,52))/2,26)；原目录：ichimoku_cloud.senkou_b（period=52）；追踪：PF01431；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
