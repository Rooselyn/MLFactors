"""Microsoft Qlib Alpha360

公式：C[t−37]/C[t]；原目录：CLOSE37；追踪：PF00323；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'qlib_close_lag37_38d', 'engine': 'market'}

@register_factor
@fixed_factor('qlib_close_lag37_38d', {})
class Factor_qlib_close_lag37_38d(PublicFactor):
    name = 'qlib_close_lag37_38d'
    description = 'C[t−37]/C[t]；原目录：CLOSE37；追踪：PF00323；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。'
    INPUTS = INPUTS
    SPEC = SPEC
