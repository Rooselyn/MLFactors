"""Stockstats

公式：完整定义为附录StockDataFrame中'inertia'对应的_get_*方法及其全部内置算子；列名='inertia'；全部类级默认参数已保留。源码算子/递推链：value.iloc[:max(window, rvgi_window) + 2] = 0；输出=value；输出=Series(zeros(len(self)), index=index)；对RVGI在指定回归窗口作线性回归，取当前拟合端点；RVGI按源式对(O,C,H,L)对称平滑后构造；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1761)；原目录：inertia（窗口=(20, 14)）；追踪：PF01481；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'stockstats_inertia_20_14d', 'root_function': 'StockDataFrame.retype', 'parameters': {'column': 'inertia'}, 'output_index': 0, 'output_label': 'inertia', 'kernel': 'kernel_34231470068a1530', 'engine': 'stockstats', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('stockstats_inertia_20_14d', {})
class Factor_stockstats_inertia_20_14d(PublicFactor):
    name = 'stockstats_inertia_20_14d'
    description = "完整定义为附录StockDataFrame中'inertia'对应的_get_*方法及其全部内置算子；列名='inertia'；全部类级默认参数已保留。源码算子/递推链：value.iloc[:max(window, rvgi_window) + 2] = 0；输出=value；输出=Series(zeros(len(self)), index=index)；对RVGI在指定回归窗口作线性回归，取当前拟合端点；RVGI按源式对(O,C,H,L)对称平滑后构造；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1761)；原目录：inertia（窗口=(20, 14)）；追踪：PF01481；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
