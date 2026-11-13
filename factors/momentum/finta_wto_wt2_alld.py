"""FinTA

公式：源码算子/递推链：esa = ap.ewm(span=average_length, adjust=adjust).mean()；d = Series((ap - esa).abs().ewm(span=channel_length, adjust=adjust).mean(), name='d')；ci = (ap - esa) / (0.015 * d)；wt1 = Series(ci.ewm(span=average_length, adjust=adjust).mean(), name='WT1.')；wt2 = Series(wt1.rolling(window=4).mean(), name='WT2.')；输出=concat([wt1, wt2], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1805)。；固定默认参数={'channel_length': 10, 'average_length': 21, 'adjust': True}；实际单列输出='WT2.'；；原目录：WTO（channel_length=10, average_length=21）；追踪：PF01023；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_wto_wt2_alld', 'root_function': 'TA.WTO', 'parameters': {'channel_length': 10, 'average_length': 21, 'adjust': True}, 'output_index': 1, 'output_label': 'WT2.', 'kernel': 'kernel_2f0892620bf561b5', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_wto_wt2_alld', {})
class Factor_finta_wto_wt2_alld(PublicFactor):
    name = 'finta_wto_wt2_alld'
    description = "源码算子/递推链：esa = ap.ewm(span=average_length, adjust=adjust).mean()；d = Series((ap - esa).abs().ewm(span=channel_length, adjust=adjust).mean(), name='d')；ci = (ap - esa) / (0.015 * d)；wt1 = Series(ci.ewm(span=average_length, adjust=adjust).mean(), name='WT1.')；wt2 = Series(wt1.rolling(window=4).mean(), name='WT2.')；输出=concat([wt1, wt2], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1805)。；固定默认参数={'channel_length': 10, 'average_length': 21, 'adjust': True}；实际单列输出='WT2.'；；原目录：WTO（channel_length=10, average_length=21）；追踪：PF01023；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
