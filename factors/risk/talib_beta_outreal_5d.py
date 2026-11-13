"""TA-Lib（技术指标及K线形态）

公式：Cov(ΔX/X[-1],ΔY/Y[-1])/Var(ΔX/X[-1])；TA-Lib/bta-lib此实现为第二输入对第一输入的斜率，若要股票对市场β须核对输入顺序；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_BETA.c)；默认参数={'Time Period': 5.0}；完整数值核及辅助调用在实现附录展开。；原目录：BETA.outReal（Time Period=5）；追踪：PF00669；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'benchmark_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(("ts_code", "000905.SH"),)),
}
SPEC = {'name': 'talib_beta_outreal_5d', 'root_function': 'TA_BETA', 'required_inputs': ['inReal0', 'inReal1'], 'parameters': {'Time Period': 5.0}, 'options': [5.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 5, 'kernel': 'kernel_88bbb7520416adef', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal0', 'double'], ['inReal1', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_beta_outreal_5d', {})
class Factor_talib_beta_outreal_5d(PublicFactor):
    name = 'talib_beta_outreal_5d'
    description = "Cov(ΔX/X[-1],ΔY/Y[-1])/Var(ΔX/X[-1])；TA-Lib/bta-lib此实现为第二输入对第一输入的斜率，若要股票对市场β须核对输入顺序；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_BETA.c)；默认参数={'Time Period': 5.0}；完整数值核及辅助调用在实现附录展开。；原目录：BETA.outReal（Time Period=5）；追踪：PF00669；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
