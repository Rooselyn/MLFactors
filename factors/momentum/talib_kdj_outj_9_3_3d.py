"""TA-Lib（技术指标及K线形态）

公式：RSV=100(C−min(L,n))/(max(H,n)−min(L,n))；K=SMA递推(RSV,3,1)，D=SMA递推(K,3,1)，J=3K−2D；本行取输出outJ。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_KDJ.c)；默认参数={'Fast-K Period': 9.0, 'Slow-K Period': 3.0, 'Slow-K MA': 13.0, 'Slow-D Period': 3.0, 'Slow-D MA': 13.0}；完整数值核及辅助调用在实现附录展开。；原目录：KDJ.outJ（Fast-K Period=9, Slow-K Period=3, Slow-K MA=13, Slow-D Period=3, Slow-D MA=13）；追踪：PF00786；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:kdj（length=9, signal=3）
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
SPEC = {'name': 'talib_kdj_outj_9_3_3d', 'root_function': 'TA_KDJ', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Fast-K Period': 9.0, 'Slow-K Period': 3.0, 'Slow-K MA': 13.0, 'Slow-D Period': 3.0, 'Slow-D MA': 13.0}, 'options': [9.0, 3.0, 13.0, 3.0, 13.0], 'outputs': ['outK', 'outD', 'outJ'], 'output_index': 2, 'output_label': 'outJ', 'warmup': 12, 'kernel': 'kernel_74e9534c47dba8e4', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInFastK_Period', 'int'], ['optInSlowK_Period', 'int'], ['optInSlowK_MAType', 'int'], ['optInSlowD_Period', 'int'], ['optInSlowD_MAType', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outK', 'double'], ['outD', 'double'], ['outJ', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_kdj_outj_9_3_3d', {})
class Factor_talib_kdj_outj_9_3_3d(PublicFactor):
    name = 'talib_kdj_outj_9_3_3d'
    description = "RSV=100(C−min(L,n))/(max(H,n)−min(L,n))；K=SMA递推(RSV,3,1)，D=SMA递推(K,3,1)，J=3K−2D；本行取输出outJ。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_KDJ.c)；默认参数={'Fast-K Period': 9.0, 'Slow-K Period': 3.0, 'Slow-K MA': 13.0, 'Slow-D Period': 3.0, 'Slow-D MA': 13.0}；完整数值核及辅助调用在实现附录展开。；原目录：KDJ.outJ（Fast-K Period=9, Slow-K Period=3, Slow-K MA=13, Slow-D Period=3, Slow-D MA=13）；追踪：PF00786；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:kdj（length=9, signal=3）"
    INPUTS = INPUTS
    SPEC = SPEC
