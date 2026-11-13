"""通联 DataYes／优矿424因子库

公式：circ_mv×10000，单位元；Neg指negotiable，不表示负号。；原目录：NegMktValue；追踪：DY0043；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'circ_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'circ_mv'),
}
SPEC = {'name': 'datayes_float_market_cap_1d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_float_market_cap_1d', {})
class Factor_datayes_float_market_cap_1d(PublicFactor):
    name = 'datayes_float_market_cap_1d'
    description = 'circ_mv×10000，单位元；Neg指negotiable，不表示负号。；原目录：NegMktValue；追踪：DY0043；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
