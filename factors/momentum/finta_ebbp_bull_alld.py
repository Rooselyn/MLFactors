"""FinTA

公式：Bull=H−EMA(C,n)，Bear=L−EMA(C,n)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1605)。；固定默认参数={}；实际单列输出='Bull.'；；原目录：EBBP（无固定窗口）；追踪：PF01015；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_ebbp_bull_alld', 'root_function': 'TA.EBBP', 'parameters': {}, 'output_index': 0, 'output_label': 'Bull.', 'kernel': 'kernel_0aef886897fc2b19', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_ebbp_bull_alld', {})
class Factor_finta_ebbp_bull_alld(PublicFactor):
    name = 'finta_ebbp_bull_alld'
    description = "Bull=H−EMA(C,n)，Bear=L−EMA(C,n)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1605)。；固定默认参数={}；实际单列输出='Bull.'；；原目录：EBBP（无固定窗口）；追踪：PF01015；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
