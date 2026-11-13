"""Stockstats

公式：完整定义为附录StockDataFrame中'close_20_z'对应的_get_*方法及其全部内置算子；列名='close_20_z'；全部类级默认参数已保留。源码算子/递推链：value = (col - mean) / std；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L790)；原目录：z（窗口=需要调用方显式指定窗口）；追踪：PF01494；[来源](https://github.com/jealous/stockstats)。
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
SPEC = {'name': 'stockstats_z_20d', 'root_function': 'StockDataFrame.retype', 'parameters': {'column': 'close_20_z'}, 'output_index': 0, 'output_label': 'close_20_z', 'kernel': 'kernel_34231470068a1530', 'engine': 'stockstats', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('stockstats_z_20d', {})
class Factor_stockstats_z_20d(PublicFactor):
    name = 'stockstats_z_20d'
    description = "完整定义为附录StockDataFrame中'close_20_z'对应的_get_*方法及其全部内置算子；列名='close_20_z'；全部类级默认参数已保留。源码算子/递推链：value = (col - mean) / std；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L790)；原目录：z（窗口=需要调用方显式指定窗口）；追踪：PF01494；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
