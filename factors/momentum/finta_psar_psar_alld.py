"""FinTA

公式：源码算子/递推链：psarbull = [None] * length；psarbear = [None] * length；输出=concat([psar, psarbull, psarbear], axis=1)；psar[i] = psar[i - 1] + af * (hp - psar[i - 1])；psar[i] = psar[i - 1] + af * (lp - psar[i - 1])；af = min(af + iaf, maxaf)；psar[i] = low[i - 1]；psar[i] = low[i - 2]；psar[i] = high[i - 1]；psar[i] = high[i - 2]；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L863)。；固定默认参数={'iaf': 0.02, 'maxaf': 0.2}；实际单列输出='psar'；将对原close视图的写入改为copy；修正原返回代码bull/bear列覆盖，按实际多/空分支分别返回对应向量。；原目录：PSAR（iaf=0.02, maxaf=0.2）；追踪：PF00989；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_psar_psar_alld', 'root_function': 'TA.PSAR', 'parameters': {'iaf': 0.02, 'maxaf': 0.2}, 'output_index': 0, 'output_label': 'psar', 'kernel': 'kernel_bea8c6cdd75580a8', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_psar_psar_alld', {})
class Factor_finta_psar_psar_alld(PublicFactor):
    name = 'finta_psar_psar_alld'
    description = "源码算子/递推链：psarbull = [None] * length；psarbear = [None] * length；输出=concat([psar, psarbull, psarbear], axis=1)；psar[i] = psar[i - 1] + af * (hp - psar[i - 1])；psar[i] = psar[i - 1] + af * (lp - psar[i - 1])；af = min(af + iaf, maxaf)；psar[i] = low[i - 1]；psar[i] = low[i - 2]；psar[i] = high[i - 1]；psar[i] = high[i - 2]；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L863)。；固定默认参数={'iaf': 0.02, 'maxaf': 0.2}；实际单列输出='psar'；将对原close视图的写入改为copy；修正原返回代码bull/bear列覆盖，按实际多/空分支分别返回对应向量。；原目录：PSAR（iaf=0.02, maxaf=0.2）；追踪：PF00989；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
