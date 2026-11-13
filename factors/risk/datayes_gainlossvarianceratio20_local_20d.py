"""通联 DataYes／优矿424因子库

公式：最近20日正收益条件样本方差/负收益条件样本方差；两组各至少2个样本。；原目录：GainLossVarianceRatio20；追踪：DY0139；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'datayes_gainlossvarianceratio20_local_20d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_gainlossvarianceratio20_local_20d', {})
class Factor_datayes_gainlossvarianceratio20_local_20d(PublicFactor):
    name = 'datayes_gainlossvarianceratio20_local_20d'
    description = '最近20日正收益条件样本方差/负收益条件样本方差；两组各至少2个样本。；原目录：GainLossVarianceRatio20；追踪：DY0139；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
