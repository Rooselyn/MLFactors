"""bta-lib

公式：y_0=C_0，y_t=(1−2/31)y_{t−1}+(2/31)C_t；原目录：ewma.ewma（period=30, adjust=False）；追踪：PF01355；[来源](https://github.com/mementum/bta-lib)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'btalib_first_seed_ewma_30d', 'engine': 'explicit', 'period': 30}

@register_factor
@fixed_factor('btalib_first_seed_ewma_30d', {})
class Factor_btalib_first_seed_ewma_30d(PublicFactor):
    name = 'btalib_first_seed_ewma_30d'
    description = 'y_0=C_0，y_t=(1−2/31)y_{t−1}+(2/31)C_t；原目录：ewma.ewma（period=30, adjust=False）；追踪：PF01355；[来源](https://github.com/mementum/bta-lib)。'
    INPUTS = INPUTS
    SPEC = SPEC
