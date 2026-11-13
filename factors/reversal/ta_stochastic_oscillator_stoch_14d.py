"""Python ta（bukosabino）

公式：100(C−min(L,n))/(max(H,n)−min(L,n))；n=14；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：StochasticOscillator.stoch（window=14, smooth_window=3）；追踪：PF00950；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:STOCH（period=14）、bta-lib:stochf.k（period=14, pfast=3）
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
SPEC = {'name': 'ta_stochastic_oscillator_stoch_14d', 'engine': 'ta', 'module': 'momentum', 'class': 'StochasticOscillator', 'getter': 'stoch', 'parameters': {}, 'minimum': 1}

@register_factor
@fixed_factor('ta_stochastic_oscillator_stoch_14d', {})
class Factor_ta_stochastic_oscillator_stoch_14d(PublicFactor):
    name = 'ta_stochastic_oscillator_stoch_14d'
    description = '100(C−min(L,n))/(max(H,n)−min(L,n))；n=14；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：StochasticOscillator.stoch（window=14, smooth_window=3）；追踪：PF00950；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:STOCH（period=14）、bta-lib:stochf.k（period=14, pfast=3）'
    INPUTS = INPUTS
    SPEC = SPEC
