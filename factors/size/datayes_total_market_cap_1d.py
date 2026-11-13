"""通联 DataYes／优矿424因子库

公式：total_mv×10000，单位元。；原目录：MktValue；追踪：DY0040；[来源](https://uqer.datayes.com/help/appendixFactors/)。；同定义来源别名：RQData／米筐因子库（公开文档核实选集）:market_cap
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'),
}
SPEC = {'name': 'datayes_total_market_cap_1d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_total_market_cap_1d', {})
class Factor_datayes_total_market_cap_1d(PublicFactor):
    name = 'datayes_total_market_cap_1d'
    description = 'total_mv×10000，单位元。；原目录：MktValue；追踪：DY0040；[来源](https://uqer.datayes.com/help/appendixFactors/)。；同定义来源别名：RQData／米筐因子库（公开文档核实选集）:market_cap'
    INPUTS = INPUTS
    SPEC = SPEC
