"""Stockstats

公式：完整定义为附录StockDataFrame中'vwma'对应的_get_*方法及其全部内置算子；列名='vwma'；全部类级默认参数已保留。sum(C×V,n)/sum(V,n)；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1412)；原目录：vwma（窗口=14）；追踪：PF01472；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'stockstats_vwma_14d', 'root_function': 'StockDataFrame.retype', 'parameters': {'column': 'vwma'}, 'output_index': 0, 'output_label': 'vwma', 'kernel': 'kernel_34231470068a1530', 'engine': 'stockstats', 'minimum': 1, 'gate_bars': 1, 'adjust_turnover_price': True}

@register_factor
@fixed_factor('stockstats_vwma_14d', {})
class Factor_stockstats_vwma_14d(PublicFactor):
    name = 'stockstats_vwma_14d'
    description = "完整定义为附录StockDataFrame中'vwma'对应的_get_*方法及其全部内置算子；列名='vwma'；全部类级默认参数已保留。sum(C×V,n)/sum(V,n)；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1412)；原目录：vwma（窗口=14）；追踪：PF01472；[来源](https://github.com/jealous/stockstats)。；本地复权适配：均价在后复权尺度计算，输入核的等效成交额=amount×1000×adj_factor；因此核内amount/volume=(amount×1000)/(vol×100)×adj_factor。"
    INPUTS = INPUTS
    SPEC = SPEC
