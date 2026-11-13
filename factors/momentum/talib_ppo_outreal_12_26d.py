"""TA-Lib（技术指标及K线形态）

公式：100×(MA(C,fast)−MA(C,slow))/MA(C,slow)；Signal=EMA(PPO,signal)；Hist=PPO−Signal；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_PPO.c)；默认参数={'Fast Period': 12.0, 'Slow Period': 26.0, 'MA Type': 1.0}；完整数值核及辅助调用在实现附录展开。；原目录：PPO.outReal（Fast Period=12, Slow Period=26, MA Type=1）；追踪：PF00828；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_ppo_outreal_12_26d', 'root_function': 'TA_PPO', 'required_inputs': ['inReal'], 'parameters': {'Fast Period': 12.0, 'Slow Period': 26.0, 'MA Type': 1.0}, 'options': [12.0, 26.0, 1.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 25, 'kernel': 'kernel_29fd8df7f6b15e94', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInFastPeriod', 'int'], ['optInSlowPeriod', 'int'], ['optInMAType', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_ppo_outreal_12_26d', {})
class Factor_talib_ppo_outreal_12_26d(PublicFactor):
    name = 'talib_ppo_outreal_12_26d'
    description = "100×(MA(C,fast)−MA(C,slow))/MA(C,slow)；Signal=EMA(PPO,signal)；Hist=PPO−Signal；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_PPO.c)；默认参数={'Fast Period': 12.0, 'Slow Period': 26.0, 'MA Type': 1.0}；完整数值核及辅助调用在实现附录展开。；原目录：PPO.outReal（Fast Period=12, Slow Period=26, MA Type=1）；追踪：PF00828；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
