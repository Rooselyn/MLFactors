"""通联 DataYes／优矿424因子库

公式：log(circ_mv×10000)，流通市值以元计且>0。；原目录：LFLO；追踪：DY0039；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'circ_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'circ_mv'),
}
SPEC = {'name': 'datayes_log_float_market_cap_1d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_log_float_market_cap_1d', {})
class Factor_datayes_log_float_market_cap_1d(PublicFactor):
    name = 'datayes_log_float_market_cap_1d'
    description = 'log(circ_mv×10000)，流通市值以元计且>0。；原目录：LFLO；追踪：DY0039；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
