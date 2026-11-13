"""TA-Lib（技术指标及K线形态）

公式：(H−L)/V；无自由窗口参数；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：MARKETFI.outReal（无窗口参数）；追踪：PF00808；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:MARKETFI.marketfi（参数：none）、Pandas TA Classic:marketfi（原函数默认参数/显式周期）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'talib_marketfi_outreal_1d', 'root_function': 'TA_MARKETFI', 'required_inputs': ['inHigh', 'inLow', 'inVolume'], 'parameters': {}, 'options': [], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 0, 'kernel': 'kernel_b2bb3ef3cdba2fec', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inVolume', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_marketfi_outreal_1d', {})
class Factor_talib_marketfi_outreal_1d(PublicFactor):
    name = 'talib_marketfi_outreal_1d'
    description = '(H−L)/V；无自由窗口参数；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：MARKETFI.outReal（无窗口参数）；追踪：PF00808；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:MARKETFI.marketfi（参数：none）、Pandas TA Classic:marketfi（原函数默认参数/显式周期）'
    INPUTS = INPUTS
    SPEC = SPEC
