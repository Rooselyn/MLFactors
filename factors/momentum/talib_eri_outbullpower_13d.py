"""TA-Lib（技术指标及K线形态）

公式：Bull=H−EMA(C,n)，Bear=L−EMA(C,n)；本行取输出outBullPower。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ERI.c)；默认参数={'Time Period': 13.0}；完整数值核及辅助调用在实现附录展开。；原目录：ERI.outBullPower（Time Period=13）；追踪：PF00757；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:eri（length=13）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_eri_outbullpower_13d', 'root_function': 'TA_ERI', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 13.0}, 'options': [13.0], 'outputs': ['outBullPower', 'outBearPower'], 'output_index': 0, 'output_label': 'outBullPower', 'warmup': 12, 'kernel': 'kernel_8a4fbc5328b9844a', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outBullPower', 'double'], ['outBearPower', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_eri_outbullpower_13d', {})
class Factor_talib_eri_outbullpower_13d(PublicFactor):
    name = 'talib_eri_outbullpower_13d'
    description = "Bull=H−EMA(C,n)，Bear=L−EMA(C,n)；本行取输出outBullPower。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_ERI.c)；默认参数={'Time Period': 13.0}；完整数值核及辅助调用在实现附录展开。；原目录：ERI.outBullPower（Time Period=13）；追踪：PF00757；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:eri（length=13）"
    INPUTS = INPUTS
    SPEC = SPEC
