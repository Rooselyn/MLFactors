"""TA-Lib（技术指标及K线形态）

公式：X=递推归一化((H+L)/2在n期极值区间的位置)，clip(X,−0.999,0.999)；F=0.5log((1+X)/(1−X))+0.5F[-1]；本行取输出outFisher。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_FISHER.c)；默认参数={'Time Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：FISHER.outFisher（Time Period=10）；追踪：PF00759；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_fisher_outfisher_10d', 'root_function': 'TA_FISHER', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Time Period': 10.0}, 'options': [10.0], 'outputs': ['outFisher', 'outTrigger'], 'output_index': 0, 'output_label': 'outFisher', 'warmup': 9, 'kernel': 'kernel_073e011158b9f668', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outFisher', 'double'], ['outTrigger', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_fisher_outfisher_10d', {})
class Factor_talib_fisher_outfisher_10d(PublicFactor):
    name = 'talib_fisher_outfisher_10d'
    description = "X=递推归一化((H+L)/2在n期极值区间的位置)，clip(X,−0.999,0.999)；F=0.5log((1+X)/(1−X))+0.5F[-1]；本行取输出outFisher。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_FISHER.c)；默认参数={'Time Period': 10.0}；完整数值核及辅助调用在实现附录展开。；原目录：FISHER.outFisher（Time Period=10）；追踪：PF00759；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
