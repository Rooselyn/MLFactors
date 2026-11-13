"""TA-Lib（技术指标及K线形态）

公式：sum(V×(2C−H−L)/(H−L),n)/sum(V,n)；n=20；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：CMF.outReal（Time Period=20）；追踪：PF00738；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:ChaikinMoneyFlowIndicator.chaikin_money_flow（window=20）、Pandas TA Classic:cmf（length=20）
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
SPEC = {'name': 'talib_cmf_20d', 'root_function': 'TA_CMF', 'required_inputs': ['inHigh', 'inLow', 'inClose', 'inVolume'], 'parameters': {'Time Period': 20.0}, 'options': [20.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 19, 'kernel': 'kernel_7f4c245a79053c85', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['inVolume', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_cmf_20d', {})
class Factor_talib_cmf_20d(PublicFactor):
    name = 'talib_cmf_20d'
    description = "sum(V×(2C−H−L)/(H−L),n)/sum(V,n)；n=20；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：CMF.outReal（Time Period=20）；追踪：PF00738；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:ChaikinMoneyFlowIndicator.chaikin_money_flow（window=20）、Pandas TA Classic:cmf（length=20）"
    INPUTS = INPUTS
    SPEC = SPEC
