"""FinTA

公式：+VI=sum(abs(H−L[-1]),n)/sum(TR,n)，−VI=sum(abs(L−H[-1]),n)/sum(TR,n)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1323)。；固定默认参数={'period': 14}；实际单列输出='VIm'；；原目录：VORTEX（period=14）；追踪：PF01004；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_vortex_vim_14d', 'root_function': 'TA.VORTEX', 'parameters': {'period': 14}, 'output_index': 0, 'output_label': 'VIm', 'kernel': 'kernel_59e7df5977c316da', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_vortex_vim_14d', {})
class Factor_finta_vortex_vim_14d(PublicFactor):
    name = 'finta_vortex_vim_14d'
    description = "+VI=sum(abs(H−L[-1]),n)/sum(TR,n)，−VI=sum(abs(L−H[-1]),n)/sum(TR,n)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1323)。；固定默认参数={'period': 14}；实际单列输出='VIm'；；原目录：VORTEX（period=14）；追踪：PF01004；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
