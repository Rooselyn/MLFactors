"""FinTA

公式：mean(C,41)；原目录：SMA（period=41）；追踪：PF00963；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_sma_41d', 'engine': 'finta', 'root_function': 'TA.SMA', 'parameters': {}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_sma_41d', {})
class Factor_finta_sma_41d(PublicFactor):
    name = 'finta_sma_41d'
    description = 'mean(C,41)；原目录：SMA（period=41）；追踪：PF00963；[来源](https://github.com/peerchemist/finta)。'
    INPUTS = INPUTS
    SPEC = SPEC
