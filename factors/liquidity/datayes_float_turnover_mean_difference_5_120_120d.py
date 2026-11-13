"""通联 DataYes／优矿424因子库

公式：T=vol×100/(float_share×10000)；mean(T,5)−mean(T,120)。官方数据字典英文明确为difference，不是相对比值。；原目录：DAVOL5；追踪：DY0003；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'float_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'float_share'),
}
SPEC = {'name': 'datayes_float_turnover_mean_difference_5_120_120d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_float_turnover_mean_difference_5_120_120d', {})
class Factor_datayes_float_turnover_mean_difference_5_120_120d(PublicFactor):
    name = 'datayes_float_turnover_mean_difference_5_120_120d'
    description = 'T=vol×100/(float_share×10000)；mean(T,5)−mean(T,120)。官方数据字典英文明确为difference，不是相对比值。；原目录：DAVOL5；追踪：DY0003；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
