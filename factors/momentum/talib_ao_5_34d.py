"""TA-Lib（技术指标及K线形态）

公式：mean((H+L)/2,5)−mean((H+L)/2,34)；无自由窗口参数；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Fast Period': 5.0, 'Slow Period': 34.0}；完整数值核及辅助调用在实现附录展开。；原目录：AO.outReal（Fast Period=5, Slow Period=34）；追踪：PF00656；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:AwesomeOscillatorIndicator.awesome_oscillator（window1=5, window2=34）、FinTA:AO（slow_period=34, fast_period=5）、Tulip Indicators:AO.ao（参数：none）、Pandas TA Classic:ao（fast=5, slow=34）、Stockstats:ao（窗口=(5, 34)）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_ao_5_34d', 'root_function': 'TA_AO', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Fast Period': 5.0, 'Slow Period': 34.0}, 'options': [5.0, 34.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 33, 'kernel': 'kernel_80b9679682541e56', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInFastPeriod', 'int'], ['optInSlowPeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_ao_5_34d', {})
class Factor_talib_ao_5_34d(PublicFactor):
    name = 'talib_ao_5_34d'
    description = "mean((H+L)/2,5)−mean((H+L)/2,34)；无自由窗口参数；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Fast Period': 5.0, 'Slow Period': 34.0}；完整数值核及辅助调用在实现附录展开。；原目录：AO.outReal（Fast Period=5, Slow Period=34）；追踪：PF00656；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:AwesomeOscillatorIndicator.awesome_oscillator（window1=5, window2=34）、FinTA:AO（slow_period=34, fast_period=5）、Tulip Indicators:AO.ao（参数：none）、Pandas TA Classic:ao（fast=5, slow=34）、Stockstats:ao（窗口=(5, 34)）"
    INPUTS = INPUTS
    SPEC = SPEC
