"""Stockstats

公式：完整定义为附录StockDataFrame中'macd'对应的_get_*方法及其全部内置算子；列名='macd'；全部类级默认参数已保留。DIF=EMA(C,fast)−EMA(C,slow)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1227)；原目录：macd（窗口=(12, 26, 9)）；追踪：PF01476；[来源](https://github.com/jealous/stockstats)。
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
SPEC = {'name': 'stockstats_macd_12_26_9d', 'root_function': 'StockDataFrame.retype', 'parameters': {'column': 'macd'}, 'output_index': 0, 'output_label': 'macd', 'kernel': 'kernel_34231470068a1530', 'engine': 'stockstats', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('stockstats_macd_12_26_9d', {})
class Factor_stockstats_macd_12_26_9d(PublicFactor):
    name = 'stockstats_macd_12_26_9d'
    description = "完整定义为附录StockDataFrame中'macd'对应的_get_*方法及其全部内置算子；列名='macd'；全部类级默认参数已保留。DIF=EMA(C,fast)−EMA(C,slow)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L1227)；原目录：macd（窗口=(12, 26, 9)）；追踪：PF01476；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
