"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：k = 2.0 / (optInTimePeriod + 1.0);；tempReal = inReal[today++];；tempReal += inReal[today++];；e1 = tempReal / optInTimePeriod;；e1 = fma(one_minus_k, e1, k * inReal[today++]);；tempReal += e1;；e2 = tempReal / optInTimePeriod;；e2 = fma(one_minus_k, e2, k * e1);；tempReal += e2;；e3 = tempReal / optInTimePeriod;；e3 = fma(one_minus_k, e3, k * e2);；tempReal += e3;；e4 = tempReal / optInTimePeriod;；e4 = fma(one_minus_k, e4, k * e3);；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_T3.c)；默认参数={'Time Period': 5.0, 'Volume Factor': 0.7}；完整数值核及辅助调用在实现附录展开。；原目录：T3.outReal（Time Period=5, Volume Factor=7.000000e-1）；追踪：PF00864；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_t3_outreal_5d', 'root_function': 'TA_T3', 'required_inputs': ['inReal'], 'parameters': {'Time Period': 5.0, 'Volume Factor': 0.7}, 'options': [5.0, 0.7], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 24, 'kernel': 'kernel_97cabcf99ef31cc6', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInTimePeriod', 'int'], ['optInVFactor', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_t3_outreal_5d', {})
class Factor_talib_t3_outreal_5d(PublicFactor):
    name = 'talib_t3_outreal_5d'
    description = "源码核心递推表达式（完整分支/参数见链接）：k = 2.0 / (optInTimePeriod + 1.0);；tempReal = inReal[today++];；tempReal += inReal[today++];；e1 = tempReal / optInTimePeriod;；e1 = fma(one_minus_k, e1, k * inReal[today++]);；tempReal += e1;；e2 = tempReal / optInTimePeriod;；e2 = fma(one_minus_k, e2, k * e1);；tempReal += e2;；e3 = tempReal / optInTimePeriod;；e3 = fma(one_minus_k, e3, k * e2);；tempReal += e3;；e4 = tempReal / optInTimePeriod;；e4 = fma(one_minus_k, e4, k * e3);；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_T3.c)；默认参数={'Time Period': 5.0, 'Volume Factor': 0.7}；完整数值核及辅助调用在实现附录展开。；原目录：T3.outReal（Time Period=5, Volume Factor=7.000000e-1）；追踪：PF00864；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
