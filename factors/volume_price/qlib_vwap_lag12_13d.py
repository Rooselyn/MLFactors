"""Microsoft Qlib Alpha360

公式：P[t−12]/C[t]；原目录：VWAP12；追踪：PF00538；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'qlib_vwap_lag12_13d', 'engine': 'market'}

@register_factor
@fixed_factor('qlib_vwap_lag12_13d', {})
class Factor_qlib_vwap_lag12_13d(PublicFactor):
    name = 'qlib_vwap_lag12_13d'
    description = 'P[t−12]/C[t]；原目录：VWAP12；追踪：PF00538；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。'
    INPUTS = INPUTS
    SPEC = SPEC
