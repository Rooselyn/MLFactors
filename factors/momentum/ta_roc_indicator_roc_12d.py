"""Python ta（bukosabino）

公式：100(C/C[-n]−1)；n=12；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：ROCIndicator.roc（window=12）；追踪：PF00953；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:ROC（period=12）、bta-lib:roc.roc（period=12）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_roc_indicator_roc_12d', 'engine': 'ta', 'module': 'momentum', 'class': 'ROCIndicator', 'getter': 'roc', 'parameters': {}, 'minimum': 1}

@register_factor
@fixed_factor('ta_roc_indicator_roc_12d', {})
class Factor_ta_roc_indicator_roc_12d(PublicFactor):
    name = 'ta_roc_indicator_roc_12d'
    description = '100(C/C[-n]−1)；n=12；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：ROCIndicator.roc（window=12）；追踪：PF00953；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:ROC（period=12）、bta-lib:roc.roc（period=12）'
    INPUTS = INPUTS
    SPEC = SPEC
