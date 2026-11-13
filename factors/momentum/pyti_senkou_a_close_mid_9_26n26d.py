"""PyTI

公式：lag((mid(C,9)+mid(C,26))/2,26)，mid(C,n)=(max(C,n)+min(C,n))/2；原目录：ichimoku_cloud.senkou_a（period等由调用方指定）；追踪：PF01430；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_senkou_a_close_mid_9_26n26d', 'engine': 'explicit', 'period': 14}

@register_factor
@fixed_factor('pyti_senkou_a_close_mid_9_26n26d', {})
class Factor_pyti_senkou_a_close_mid_9_26n26d(PublicFactor):
    name = 'pyti_senkou_a_close_mid_9_26n26d'
    description = 'lag((mid(C,9)+mid(C,26))/2,26)，mid(C,n)=(max(C,n)+min(C,n))/2；原目录：ichimoku_cloud.senkou_a（period等由调用方指定）；追踪：PF01430；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
