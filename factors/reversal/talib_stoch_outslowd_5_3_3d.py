"""TA-Lib（技术指标及K线形态）

公式：FastK=100(C−min(L,n))/(max(H,n)−min(L,n))；SlowK=MA(FastK,k)；SlowD=MA(SlowK,d)；本行取输出outSlowD。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_STOCH.c)；默认参数={'Fast-K Period': 5.0, 'Slow-K Period': 3.0, 'Slow-K MA': 0.0, 'Slow-D Period': 3.0, 'Slow-D MA': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：STOCH.outSlowD（Fast-K Period=5, Slow-K Period=3, Slow-K MA=0, Slow-D Period=3, Slow-D MA=0）；追踪：PF00852；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
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
SPEC = {'name': 'talib_stoch_outslowd_5_3_3d', 'root_function': 'TA_STOCH', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Fast-K Period': 5.0, 'Slow-K Period': 3.0, 'Slow-K MA': 0.0, 'Slow-D Period': 3.0, 'Slow-D MA': 0.0}, 'options': [5.0, 3.0, 0.0, 3.0, 0.0], 'outputs': ['outSlowK', 'outSlowD'], 'output_index': 1, 'output_label': 'outSlowD', 'warmup': 8, 'kernel': 'kernel_e00ad70e8c633cc7', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInFastK_Period', 'int'], ['optInSlowK_Period', 'int'], ['optInSlowK_MAType', 'int'], ['optInSlowD_Period', 'int'], ['optInSlowD_MAType', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outSlowK', 'double'], ['outSlowD', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_stoch_outslowd_5_3_3d', {})
class Factor_talib_stoch_outslowd_5_3_3d(PublicFactor):
    name = 'talib_stoch_outslowd_5_3_3d'
    description = "FastK=100(C−min(L,n))/(max(H,n)−min(L,n))；SlowK=MA(FastK,k)；SlowD=MA(SlowK,d)；本行取输出outSlowD。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_STOCH.c)；默认参数={'Fast-K Period': 5.0, 'Slow-K Period': 3.0, 'Slow-K MA': 0.0, 'Slow-D Period': 3.0, 'Slow-D MA': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：STOCH.outSlowD（Fast-K Period=5, Slow-K Period=3, Slow-K MA=0, Slow-D Period=3, Slow-D MA=0）；追踪：PF00852；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
