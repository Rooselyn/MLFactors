"""Stockstats

公式：完整定义为附录StockDataFrame中'ftr'对应的_get_*方法及其全部内置算子；列名='ftr'；全部类级默认参数已保留。X=递推归一化((H+L)/2在n期极值区间的位置)，clip(X,−0.999,0.999)；F=0.5log((1+X)/(1−X))+0.5F[-1]；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1655)；原目录：ftr（窗口=9）；追踪：PF01503；[来源](https://github.com/jealous/stockstats)。
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
SPEC = {'name': 'stockstats_ftr_9d', 'root_function': 'StockDataFrame.retype', 'parameters': {'column': 'ftr'}, 'output_index': 0, 'output_label': 'ftr', 'kernel': 'kernel_34231470068a1530', 'engine': 'stockstats', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('stockstats_ftr_9d', {})
class Factor_stockstats_ftr_9d(PublicFactor):
    name = 'stockstats_ftr_9d'
    description = "完整定义为附录StockDataFrame中'ftr'对应的_get_*方法及其全部内置算子；列名='ftr'；全部类级默认参数已保留。X=递推归一化((H+L)/2在n期极值区间的位置)，clip(X,−0.999,0.999)；F=0.5log((1+X)/(1−X))+0.5F[-1]；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1655)；原目录：ftr（窗口=9）；追踪：PF01503；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
