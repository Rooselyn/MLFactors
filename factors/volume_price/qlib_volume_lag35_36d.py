"""Microsoft Qlib Alpha360

公式：V[t−35]/V[t]；原目录：VOLUME35；追踪：PF00621；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'qlib_volume_lag35_36d', 'engine': 'market'}

@register_factor
@fixed_factor('qlib_volume_lag35_36d', {})
class Factor_qlib_volume_lag35_36d(PublicFactor):
    name = 'qlib_volume_lag35_36d'
    description = 'V[t−35]/V[t]；原目录：VOLUME35；追踪：PF00621；[来源](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)。'
    INPUTS = INPUTS
    SPEC = SPEC
