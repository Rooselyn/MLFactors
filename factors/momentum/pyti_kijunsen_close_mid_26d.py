"""PyTI

公式：(max(C,26)+min(C,26))/2；原目录：ichimoku_cloud.kijunsen（period=26）；追踪：PF01428；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_kijunsen_close_mid_26d', 'engine': 'explicit', 'period': 26}

@register_factor
@fixed_factor('pyti_kijunsen_close_mid_26d', {})
class Factor_pyti_kijunsen_close_mid_26d(PublicFactor):
    name = 'pyti_kijunsen_close_mid_26d'
    description = '(max(C,26)+min(C,26))/2；原目录：ichimoku_cloud.kijunsen（period=26）；追踪：PF01428；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
