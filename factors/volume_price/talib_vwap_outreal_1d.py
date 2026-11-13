"""TA-Lib（技术指标及K线形态）

公式：典型价格TP=(H+L+C)/3；sum(TP×V)/sum(V)，按来源的滚动或会话锚定；不等于实际amount/vol；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_VWAP.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：VWAP.outReal（无窗口参数）；追踪：PF00878；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'talib_vwap_outreal_1d', 'root_function': 'TA_VWAP', 'required_inputs': ['inHigh', 'inLow', 'inClose', 'inVolume'], 'parameters': {}, 'options': [], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 0, 'kernel': 'kernel_375d3e03471bbb03', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['inVolume', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_vwap_outreal_1d', {})
class Factor_talib_vwap_outreal_1d(PublicFactor):
    name = 'talib_vwap_outreal_1d'
    description = '典型价格TP=(H+L+C)/3；sum(TP×V)/sum(V)，按来源的滚动或会话锚定；不等于实际amount/vol；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_VWAP.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：VWAP.outReal（无窗口参数）；追踪：PF00878；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。'
    INPUTS = INPUTS
    SPEC = SPEC
