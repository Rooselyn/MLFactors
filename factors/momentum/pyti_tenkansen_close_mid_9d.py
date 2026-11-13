"""PyTI

公式：(max(C,9)+min(C,9))/2；原目录：ichimoku_cloud.tenkansen（period=9）；追踪：PF01427；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_tenkansen_close_mid_9d', 'engine': 'explicit', 'period': 9}

@register_factor
@fixed_factor('pyti_tenkansen_close_mid_9d', {})
class Factor_pyti_tenkansen_close_mid_9d(PublicFactor):
    name = 'pyti_tenkansen_close_mid_9d'
    description = '(max(C,9)+min(C,9))/2；原目录：ichimoku_cloud.tenkansen（period=9）；追踪：PF01427；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
