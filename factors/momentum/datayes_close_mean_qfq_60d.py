"""通联 DataYes／优矿424因子库

公式：MA60(t)=mean(close[s]×adj_factor[s], s=t−59…t)/adj_factor[t]。即以t为锚的前复权均线，末日价格不调整。；原目录：MA60；追踪：DY0334；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_close_mean_qfq_60d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_close_mean_qfq_60d', {})
class Factor_datayes_close_mean_qfq_60d(PublicFactor):
    name = 'datayes_close_mean_qfq_60d'
    description = 'MA60(t)=mean(close[s]×adj_factor[s], s=t−59…t)/adj_factor[t]。即以t为锚的前复权均线，末日价格不调整。；原目录：MA60；追踪：DY0334；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
