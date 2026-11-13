"""TA-Lib（技术指标及K线形态）

公式：(max(C,n)−min(C,n))/sum(abs(ΔC),n)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_VHF.c)；默认参数={'Time Period': 28.0}；完整数值核及辅助调用在实现附录展开。；原目录：VHF.outReal（Time Period=28）；追踪：PF00874；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:vhf（length=28）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_vhf_28d', 'root_function': 'TA_VHF', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 28.0}, 'options': [28.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 28, 'kernel': 'kernel_6bcbb92556e004ce', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_vhf_28d', {})
class Factor_talib_vhf_28d(PublicFactor):
    name = 'talib_vhf_28d'
    description = "(max(C,n)−min(C,n))/sum(abs(ΔC),n)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_VHF.c)；默认参数={'Time Period': 28.0}；完整数值核及辅助调用在实现附录展开。；原目录：VHF.outReal（Time Period=28）；追踪：PF00874；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:vhf（length=28）"
    INPUTS = INPUTS
    SPEC = SPEC
