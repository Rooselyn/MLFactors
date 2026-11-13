"""Microsoft Qlib Alpha360

公式：H[t−59]/C[t]；原目录：HIGH59；追踪：PF00465；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'qlib_high_lag59_60d', 'engine': 'market'}

@register_factor
@fixed_factor('qlib_high_lag59_60d', {})
class Factor_qlib_high_lag59_60d(PublicFactor):
    name = 'qlib_high_lag59_60d'
    description = 'H[t−59]/C[t]；原目录：HIGH59；追踪：PF00465；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。'
    INPUTS = INPUTS
    SPEC = SPEC
