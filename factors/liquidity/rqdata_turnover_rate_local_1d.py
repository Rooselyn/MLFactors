"""RQData／米筐因子库（公开文档核实选集）

公式：vol×100/(float_share×10000)，当日无限售流通口径、小数。；原目录：turnover_rate；追踪：PF02693；[来源](https://www.ricequant.com/doc/rqdata/python/stock-mod.html)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'float_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'float_share'),
}
SPEC = {'name': 'rqdata_turnover_rate_local_1d', 'engine': 'market'}

@register_factor
@fixed_factor('rqdata_turnover_rate_local_1d', {})
class Factor_rqdata_turnover_rate_local_1d(PublicFactor):
    name = 'rqdata_turnover_rate_local_1d'
    description = 'vol×100/(float_share×10000)，当日无限售流通口径、小数。；原目录：turnover_rate；追踪：PF02693；[来源](https://www.ricequant.com/doc/rqdata/python/stock-mod.html)。'
    INPUTS = INPUTS
    SPEC = SPEC
