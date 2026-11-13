"""TA-Lib（技术指标及K线形态）

公式：mean(C,n)；n=20；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 20.0, 'Deviations up': 2.0, 'Deviations down': 2.0, 'MA Type': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：BBANDS.outRealMiddleBand（Time Period=20, Deviations up=2.000000e+0, Deviations down=2.000000e+0, MA Type=0）；追踪：PF00666；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:BollingerBands.bollinger_mavg（window=20, window_dev=2）、bta-lib:bbands.mid（period=20, devs=2.0）、FinTA:BBANDS（period=20, MA=None, std_multiplier=2）、Tulip Indicators:BBANDS.bbands_middle（参数：period, stddev）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_bbands_middle_band_20d', 'root_function': 'TA_BBANDS', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 20.0, 'Deviations up': 2.0, 'Deviations down': 2.0, 'MA Type': 0.0}, 'options': [20.0, 2.0, 2.0, 0.0], 'outputs': ['outRealUpperBand', 'outRealMiddleBand', 'outRealLowerBand'], 'output_index': 1, 'output_label': 'outRealMiddleBand', 'warmup': 19, 'kernel': 'kernel_1cd607b43966d09e', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInNbDevUp', 'double'], ['optInNbDevDn', 'double'], ['optInMAType', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outRealUpperBand', 'double'], ['outRealMiddleBand', 'double'], ['outRealLowerBand', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_bbands_middle_band_20d', {})
class Factor_talib_bbands_middle_band_20d(PublicFactor):
    name = 'talib_bbands_middle_band_20d'
    description = "mean(C,n)；n=20；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 20.0, 'Deviations up': 2.0, 'Deviations down': 2.0, 'MA Type': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：BBANDS.outRealMiddleBand（Time Period=20, Deviations up=2.000000e+0, Deviations down=2.000000e+0, MA Type=0）；追踪：PF00666；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:BollingerBands.bollinger_mavg（window=20, window_dev=2）、bta-lib:bbands.mid（period=20, devs=2.0）、FinTA:BBANDS（period=20, MA=None, std_multiplier=2）、Tulip Indicators:BBANDS.bbands_middle（参数：period, stddev）"
    INPUTS = INPUTS
    SPEC = SPEC
