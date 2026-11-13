"""Stockstats

公式：完整定义为附录StockDataFrame中'kst'对应的_get_*方法及其全部内置算子；列名='kst'；全部类级默认参数已保留。Σ_{i=1}^4 i×SMA(ROC(C,roc_i),sma_i)；Signal=SMA(KST,signal)；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1789)；原目录：kst（窗口=需要调用方显式指定窗口）；追踪：PF01479；[来源](https://github.com/jealous/stockstats)。
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
SPEC = {'name': 'stockstats_kst_10_15_20_30_10_10_10_15d', 'root_function': 'StockDataFrame.retype', 'parameters': {'column': 'kst'}, 'output_index': 0, 'output_label': 'kst', 'kernel': 'kernel_34231470068a1530', 'engine': 'stockstats', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('stockstats_kst_10_15_20_30_10_10_10_15d', {})
class Factor_stockstats_kst_10_15_20_30_10_10_10_15d(PublicFactor):
    name = 'stockstats_kst_10_15_20_30_10_10_10_15d'
    description = "完整定义为附录StockDataFrame中'kst'对应的_get_*方法及其全部内置算子；列名='kst'；全部类级默认参数已保留。Σ_{i=1}^4 i×SMA(ROC(C,roc_i),sma_i)；Signal=SMA(KST,signal)；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1789)；原目录：kst（窗口=需要调用方显式指定窗口）；追踪：PF01479；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
