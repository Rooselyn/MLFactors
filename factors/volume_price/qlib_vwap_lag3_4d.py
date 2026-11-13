"""Microsoft Qlib Alpha360

公式：P[t−3]/C[t]；原目录：VWAP3；追踪：PF00529；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。
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
SPEC = {'name': 'qlib_vwap_lag3_4d', 'engine': 'market'}

@register_factor
@fixed_factor('qlib_vwap_lag3_4d', {})
class Factor_qlib_vwap_lag3_4d(PublicFactor):
    name = 'qlib_vwap_lag3_4d'
    description = 'P[t−3]/C[t]；原目录：VWAP3；追踪：PF00529；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。'
    INPUTS = INPUTS
    SPEC = SPEC
