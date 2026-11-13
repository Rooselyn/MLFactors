"""FinTA

公式：E(x)=x.ewm(alpha=0.2,adjust=True,ignore_na=False,min_periods=0).mean()；E(C)；原目录：EMA（period=9）；追踪：PF00966；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_ema_9d', 'engine': 'finta', 'root_function': 'TA.EMA', 'parameters': {}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_ema_9d', {})
class Factor_finta_ema_9d(PublicFactor):
    name = 'finta_ema_9d'
    description = 'E(x)=x.ewm(alpha=0.2,adjust=True,ignore_na=False,min_periods=0).mean()；E(C)；原目录：EMA（period=9）；追踪：PF00966；[来源](https://github.com/peerchemist/finta)。'
    INPUTS = INPUTS
    SPEC = SPEC
