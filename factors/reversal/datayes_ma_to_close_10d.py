"""通联 DataYes／优矿424因子库

公式：mean(close×adj_factor,10)/(close[t]×adj_factor[t])，即前复权MA10/当日未复权收盘价。；原目录：MA10Close；追踪：DY0330；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_ma_to_close_10d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_ma_to_close_10d', {})
class Factor_datayes_ma_to_close_10d(PublicFactor):
    name = 'datayes_ma_to_close_10d'
    description = 'mean(close×adj_factor,10)/(close[t]×adj_factor[t])，即前复权MA10/当日未复权收盘价。；原目录：MA10Close；追踪：DY0330；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
