"""Microsoft Qlib Alpha360

公式：L[t−11]/C[t]；原目录：LOW11；追踪：PF00477；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'qlib_low_lag11_12d', 'engine': 'market'}

@register_factor
@fixed_factor('qlib_low_lag11_12d', {})
class Factor_qlib_low_lag11_12d(PublicFactor):
    name = 'qlib_low_lag11_12d'
    description = 'L[t−11]/C[t]；原目录：LOW11；追踪：PF00477；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。'
    INPUTS = INPUTS
    SPEC = SPEC
