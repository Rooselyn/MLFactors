"""Python ta（bukosabino）

公式：Σ_{j=0…n−1}(n−j)C[t−j]/(n(n+1)/2)；n=9；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：WMAIndicator.wma（window=9）；追踪：PF00912；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:WMA（period=9）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_wma_indicator_wma_9d', 'engine': 'ta', 'module': 'trend', 'class': 'WMAIndicator', 'getter': 'wma', 'parameters': {}, 'minimum': 1}

@register_factor
@fixed_factor('ta_wma_indicator_wma_9d', {})
class Factor_ta_wma_indicator_wma_9d(PublicFactor):
    name = 'ta_wma_indicator_wma_9d'
    description = 'Σ_{j=0…n−1}(n−j)C[t−j]/(n(n+1)/2)；n=9；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：WMAIndicator.wma（window=9）；追踪：PF00912；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:WMA（period=9）'
    INPUTS = INPUTS
    SPEC = SPEC
