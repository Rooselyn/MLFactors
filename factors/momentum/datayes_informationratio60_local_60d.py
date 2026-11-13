"""通联 DataYes／优矿424因子库

公式：主动收益E=股票简单日收益−中证500简单日收益；sqrt(252)×mean(E,N)/std(E,N,ddof=1)；基准固定中证500，非全市场。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：InformationRatio60；追踪：DY0147；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'benchmark_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(("ts_code", "000905.SH"),)),
}
SPEC = {'name': 'datayes_informationratio60_local_60d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'information_ratio', 'n': 60, 'output': 0}, 'supplied_parameters': {'kind': 'information_ratio', 'n': 60, 'output': 0}, 'output_index': 0, 'output_label': 'InformationRatio60', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_informationratio60_local_60d', {})
class Factor_datayes_informationratio60_local_60d(PublicFactor):
    name = 'datayes_informationratio60_local_60d'
    description = '主动收益E=股票简单日收益−中证500简单日收益；sqrt(252)×mean(E,N)/std(E,N,ddof=1)；基准固定中证500，非全市场。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：InformationRatio60；追踪：DY0147；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
