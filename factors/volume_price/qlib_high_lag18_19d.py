"""Microsoft Qlib Alpha360

公式：H[t−18]/C[t]；原目录：HIGH18；追踪：PF00424；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'qlib_high_lag18_19d', 'engine': 'market'}

@register_factor
@fixed_factor('qlib_high_lag18_19d', {})
class Factor_qlib_high_lag18_19d(PublicFactor):
    name = 'qlib_high_lag18_19d'
    description = 'H[t−18]/C[t]；原目录：HIGH18；追踪：PF00424；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。'
    INPUTS = INPUTS
    SPEC = SPEC
