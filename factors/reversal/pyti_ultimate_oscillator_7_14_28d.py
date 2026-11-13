"""PyTI

公式：BP=C−min(L,C[-1])；TR=max(H−L,abs(H−C[-1]),abs(L−C[-1]))；A_n=sum(BP,n)/sum(TR,n)；100(4A_7+2A_14+A_28)/7；原目录：ultimate_oscillator.ultimate_oscillator（period等由调用方指定）；追踪：PF01460；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'pyti_ultimate_oscillator_7_14_28d', 'engine': 'explicit', 'period': 28}

@register_factor
@fixed_factor('pyti_ultimate_oscillator_7_14_28d', {})
class Factor_pyti_ultimate_oscillator_7_14_28d(PublicFactor):
    name = 'pyti_ultimate_oscillator_7_14_28d'
    description = 'BP=C−min(L,C[-1])；TR=max(H−L,abs(H−C[-1]),abs(L−C[-1]))；A_n=sum(BP,n)/sum(TR,n)；100(4A_7+2A_14+A_28)/7；原目录：ultimate_oscillator.ultimate_oscillator（period等由调用方指定）；追踪：PF01460；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
