"""通联 DataYes／优矿424因子库

公式：T[s]=(vol[s]×100)/(float_share[s]×10000)；VOL20=mean(T,20)。流通口径，单位为小数。；原目录：VOL20；追踪：DY0025；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'float_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'float_share'),
}
SPEC = {'name': 'datayes_float_share_turnover_mean_20d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_float_share_turnover_mean_20d', {})
class Factor_datayes_float_share_turnover_mean_20d(PublicFactor):
    name = 'datayes_float_share_turnover_mean_20d'
    description = 'T[s]=(vol[s]×100)/(float_share[s]×10000)；VOL20=mean(T,20)。流通口径，单位为小数。；原目录：VOL20；追踪：DY0025；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
