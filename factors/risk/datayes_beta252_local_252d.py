"""通联 DataYes／优矿424因子库

公式：R=C/C[-1]−1，B=中证500close/close[-1]−1；最近N日cov(R,B,ddof=1)/var(B,ddof=1)，含截距OLS斜率。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：Beta252；追踪：DY0134；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'benchmark_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(("ts_code", "000905.SH"),)),
}
SPEC = {'name': 'datayes_beta252_local_252d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'beta', 'n': 252, 'output': 0}, 'supplied_parameters': {'kind': 'beta', 'n': 252, 'output': 0}, 'output_index': 0, 'output_label': 'Beta252', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_beta252_local_252d', {})
class Factor_datayes_beta252_local_252d(PublicFactor):
    name = 'datayes_beta252_local_252d'
    description = 'R=C/C[-1]−1，B=中证500close/close[-1]−1；最近N日cov(R,B,ddof=1)/var(B,ddof=1)，含截距OLS斜率。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：Beta252；追踪：DY0134；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
