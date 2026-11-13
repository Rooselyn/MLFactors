"""TA-Lib（技术指标及K线形态）

公式：(Upper−Lower)/Middle；是否乘100按来源；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_BBW.c)；默认参数={'Time Period': 20.0, 'Deviations up': 2.0, 'Deviations down': 2.0, 'MA Type': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：BBW.outReal（Time Period=20, Deviations up=2.000000e+0, Deviations down=2.000000e+0, MA Type=0）；追踪：PF00668；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_bbw_20d', 'root_function': 'TA_BBW', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 20.0, 'Deviations up': 2.0, 'Deviations down': 2.0, 'MA Type': 0.0}, 'options': [20.0, 2.0, 2.0, 0.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 19, 'kernel': 'kernel_a79dfd9e3db52a47', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInNbDevUp', 'double'], ['optInNbDevDn', 'double'], ['optInMAType', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_bbw_20d', {})
class Factor_talib_bbw_20d(PublicFactor):
    name = 'talib_bbw_20d'
    description = "(Upper−Lower)/Middle；是否乘100按来源；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_BBW.c)；默认参数={'Time Period': 20.0, 'Deviations up': 2.0, 'Deviations down': 2.0, 'MA Type': 0.0}；完整数值核及辅助调用在实现附录展开。；原目录：BBW.outReal（Time Period=20, Deviations up=2.000000e+0, Deviations down=2.000000e+0, MA Type=0）；追踪：PF00668；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
