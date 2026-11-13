"""PyTI

公式：完整数值定义为附录独立函数pyti_rate_of_change_rate_of_change；固定参数={'period': 14}；原目录定义：100(C/C[-n]−1)；n=N，周期由调用方指定；本条为参数化定义，不能当作任意固定窗口已实现；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：rate_of_change.rate_of_change（period等由调用方指定）；追踪：PF01446；[来源](https://github.com/kylejusticemagnuson/pyti)。；同定义来源别名：Stockstats:roc（窗口=需要调用方显式指定窗口）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_rate_of_change_14d', 'root_function': 'pyti_rate_of_change_rate_of_change', 'required_inputs': ['data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'rate_of_change', 'kernel': 'kernel_a2fb724a614b72cd', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_rate_of_change_14d', {})
class Factor_pyti_rate_of_change_14d(PublicFactor):
    name = 'pyti_rate_of_change_14d'
    description = "完整数值定义为附录独立函数pyti_rate_of_change_rate_of_change；固定参数={'period': 14}；原目录定义：100(C/C[-n]−1)；n=N，周期由调用方指定；本条为参数化定义，不能当作任意固定窗口已实现；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：rate_of_change.rate_of_change（period等由调用方指定）；追踪：PF01446；[来源](https://github.com/kylejusticemagnuson/pyti)。；同定义来源别名：Stockstats:roc（窗口=需要调用方显式指定窗口）"
    INPUTS = INPUTS
    SPEC = SPEC
