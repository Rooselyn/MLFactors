"""通联 DataYes／优矿424因子库

公式：TP=(high_hfq+low_hfq+close_hfq)/3；M=mean(TP,10)；D=mean(abs(TP_s−M_t),同一10日窗口)；CCI=(TP_t−M_t)/(0.015D)。；原目录：CCI10；追踪：DY0254；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'datayes_cci_10d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_cci_10d', {})
class Factor_datayes_cci_10d(PublicFactor):
    name = 'datayes_cci_10d'
    description = 'TP=(high_hfq+low_hfq+close_hfq)/3；M=mean(TP,10)；D=mean(abs(TP_s−M_t),同一10日窗口)；CCI=(TP_t−M_t)/(0.015D)。；原目录：CCI10；追踪：DY0254；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
