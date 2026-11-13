"""TA-Lib（技术指标及K线形态）

公式：C[t−floor(n/2)−1]−mean(C,n)；用于时点t，不能将此输出回填到较早日期；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_DPO.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：DPO.outReal（Time Period=20）；追踪：PF00751；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:DPO.dpo（参数：period）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_dpo_outreal_20d', 'root_function': 'TA_DPO', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 20.0}, 'options': [20.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 19, 'kernel': 'kernel_86e9e1370835f088', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_dpo_outreal_20d', {})
class Factor_talib_dpo_outreal_20d(PublicFactor):
    name = 'talib_dpo_outreal_20d'
    description = "C[t−floor(n/2)−1]−mean(C,n)；用于时点t，不能将此输出回填到较早日期；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_DPO.c)；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：DPO.outReal（Time Period=20）；追踪：PF00751；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:DPO.dpo（参数：period）"
    INPUTS = INPUTS
    SPEC = SPEC
