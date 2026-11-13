"""TA-Lib（技术指标及K线形态）

公式：+VI=sum(abs(H−L[-1]),n)/sum(TR,n)，−VI=sum(abs(L−H[-1]),n)/sum(TR,n)；本行取输出outMinusVI。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_VORTEX.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：VORTEX.outMinusVI（Time Period=14）；追踪：PF00877；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:vortex（length=14）
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
SPEC = {'name': 'talib_vortex_outminusvi_14d', 'root_function': 'TA_VORTEX', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 14.0}, 'options': [14.0], 'outputs': ['outPlusVI', 'outMinusVI'], 'output_index': 1, 'output_label': 'outMinusVI', 'warmup': 14, 'kernel': 'kernel_583e12407e330d59', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outPlusVI', 'double'], ['outMinusVI', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_vortex_outminusvi_14d', {})
class Factor_talib_vortex_outminusvi_14d(PublicFactor):
    name = 'talib_vortex_outminusvi_14d'
    description = "+VI=sum(abs(H−L[-1]),n)/sum(TR,n)，−VI=sum(abs(L−H[-1]),n)/sum(TR,n)；本行取输出outMinusVI。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_VORTEX.c)；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：VORTEX.outMinusVI（Time Period=14）；追踪：PF00877；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:vortex（length=14）"
    INPUTS = INPUTS
    SPEC = SPEC
