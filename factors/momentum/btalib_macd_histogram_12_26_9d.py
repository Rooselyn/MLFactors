"""bta-lib

公式：EMA_n第一个n项有效C均值为种子，之后α=2/(n+1)递推；F=EMA_12(C)，S=EMA_26(C)，D=F−S，G=EMA_9(D)，H=D−G；仅输出H；原目录：macd.histogram（pfast=12, pslow=26, psignal=9）；追踪：PF01368；[来源](https://github.com/mementum/bta-lib)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'btalib_macd_histogram_12_26_9d', 'engine': 'explicit', 'period': 9}

@register_factor
@fixed_factor('btalib_macd_histogram_12_26_9d', {})
class Factor_btalib_macd_histogram_12_26_9d(PublicFactor):
    name = 'btalib_macd_histogram_12_26_9d'
    description = 'EMA_n第一个n项有效C均值为种子，之后α=2/(n+1)递推；F=EMA_12(C)，S=EMA_26(C)，D=F−S，G=EMA_9(D)，H=D−G；仅输出H；原目录：macd.histogram（pfast=12, pslow=26, psignal=9）；追踪：PF01368；[来源](https://github.com/mementum/bta-lib)。'
    INPUTS = INPUTS
    SPEC = SPEC
