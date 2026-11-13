"""Microsoft Qlib Alpha360

公式：O[t−25]/C[t]；原目录：OPEN25；追踪：PF00371；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'qlib_open_lag25_26d', 'engine': 'market'}

@register_factor
@fixed_factor('qlib_open_lag25_26d', {})
class Factor_qlib_open_lag25_26d(PublicFactor):
    name = 'qlib_open_lag25_26d'
    description = 'O[t−25]/C[t]；原目录：OPEN25；追踪：PF00371；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。'
    INPUTS = INPUTS
    SPEC = SPEC
