"""bta-lib

公式：EMA_n第一个n项有效C均值为种子，之后α=2/(n+1)递推；EMA_12(C)−EMA_26(C)；原目录：apo.apo（pfast=12, pslow=26）；追踪：PF01376；[来源](https://github.com/mementum/bta-lib)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'btalib_apo_ema_12_26d', 'engine': 'explicit', 'period': 26}

@register_factor
@fixed_factor('btalib_apo_ema_12_26d', {})
class Factor_btalib_apo_ema_12_26d(PublicFactor):
    name = 'btalib_apo_ema_12_26d'
    description = 'EMA_n第一个n项有效C均值为种子，之后α=2/(n+1)递推；EMA_12(C)−EMA_26(C)；原目录：apo.apo（pfast=12, pslow=26）；追踪：PF01376；[来源](https://github.com/mementum/bta-lib)。'
    INPUTS = INPUTS
    SPEC = SPEC
