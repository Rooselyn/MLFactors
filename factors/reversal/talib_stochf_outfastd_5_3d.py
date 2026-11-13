"""TA-Lib（技术指标及K线形态）

公式：FastK=100(C−min(L,n))/(max(H,n)−min(L,n))；FastD=MA(FastK,d)；本行取输出outFastD。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_STOCHF.c)；默认参数={'Fast-K Period': 5.0, 'Fast-D Period': 3.0, 'Fast-D MA': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：STOCHF.outFastD（Fast-K Period=5, Fast-D Period=3, Fast-D MA=0）；追踪：PF00854；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:stochf（mamode='sma'）
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
SPEC = {'name': 'talib_stochf_outfastd_5_3d', 'root_function': 'TA_STOCHF', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Fast-K Period': 5.0, 'Fast-D Period': 3.0, 'Fast-D MA': 0.0}, 'options': [5.0, 3.0, 0.0], 'outputs': ['outFastK', 'outFastD'], 'output_index': 1, 'output_label': 'outFastD', 'warmup': 6, 'kernel': 'kernel_95950af345699310', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInFastK_Period', 'int'], ['optInFastD_Period', 'int'], ['optInFastD_MAType', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outFastK', 'double'], ['outFastD', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_stochf_outfastd_5_3d', {})
class Factor_talib_stochf_outfastd_5_3d(PublicFactor):
    name = 'talib_stochf_outfastd_5_3d'
    description = "FastK=100(C−min(L,n))/(max(H,n)−min(L,n))；FastD=MA(FastK,d)；本行取输出outFastD。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_STOCHF.c)；默认参数={'Fast-K Period': 5.0, 'Fast-D Period': 3.0, 'Fast-D MA': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：STOCHF.outFastD（Fast-K Period=5, Fast-D Period=3, Fast-D MA=0）；追踪：PF00854；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:stochf（mamode='sma'）"
    INPUTS = INPUTS
    SPEC = SPEC
