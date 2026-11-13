"""Stockstats

公式：完整定义为附录StockDataFrame中'cr'对应的_get_*方法及其全部内置算子；列名='cr'；全部类级默认参数已保留。源码算子/递推链：输出=to_series(tp)；tp = amount.values / volume.values；total = close.values + high.values + low.values；tp = total / 3.0；源码算子/递推链：输出=s_shift(cr_sma, -int(window / 2.5 + 1))；源码算子/递推链：输出=s_shift(cr_sma, -int(window / 2.5 + 1))；源码算子/递推链：输出=s_shift(cr_sma, -int(window / 2.5 + 1))；源码算子/递推链：last_middle = s_shift(middle, -1)；ym = s_shift(middle, -1)；p1 = mov_sum(high - p1_m, window)；p2 = mov_sum(ym - p2_m, window)；self[name] = cr = p1 / p2 * 100；self[f'{name}-ma1'] = _shifted_cr_sma(cr, CR_MA[0])；self[f'{name}-ma2'] = _shifted_cr_sma(cr, CR_MA[1])；self[f'{name}-ma3'] = _shifted_cr_sma(cr, CR_MA[2])；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L943)；原目录：cr（窗口=26）；追踪：PF01486；[来源](https://github.com/jealous/stockstats)。
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
SPEC = {'name': 'stockstats_cr_26d', 'root_function': 'StockDataFrame.retype', 'parameters': {'column': 'cr'}, 'output_index': 0, 'output_label': 'cr', 'kernel': 'kernel_34231470068a1530', 'engine': 'stockstats', 'minimum': 1, 'gate_bars': 1, 'adjust_turnover_price': True}

@register_factor
@fixed_factor('stockstats_cr_26d', {})
class Factor_stockstats_cr_26d(PublicFactor):
    name = 'stockstats_cr_26d'
    description = "完整定义为附录StockDataFrame中'cr'对应的_get_*方法及其全部内置算子；列名='cr'；全部类级默认参数已保留。源码算子/递推链：输出=to_series(tp)；tp = amount.values / volume.values；total = close.values + high.values + low.values；tp = total / 3.0；源码算子/递推链：输出=s_shift(cr_sma, -int(window / 2.5 + 1))；源码算子/递推链：输出=s_shift(cr_sma, -int(window / 2.5 + 1))；源码算子/递推链：输出=s_shift(cr_sma, -int(window / 2.5 + 1))；源码算子/递推链：last_middle = s_shift(middle, -1)；ym = s_shift(middle, -1)；p1 = mov_sum(high - p1_m, window)；p2 = mov_sum(ym - p2_m, window)；self[name] = cr = p1 / p2 * 100；self[f'{name}-ma1'] = _shifted_cr_sma(cr, CR_MA[0])；self[f'{name}-ma2'] = _shifted_cr_sma(cr, CR_MA[1])；self[f'{name}-ma3'] = _shifted_cr_sma(cr, CR_MA[2])；默认参数取源码_dft_windows/方法元数据；[源码](https://github.com/jealous/stockstats/blob/67318d90e2e051aeb7838b56feacf90747fd6635/stockstats.py#L943)；原目录：cr（窗口=26）；追踪：PF01486；[来源](https://github.com/jealous/stockstats)。；本地复权适配：均价在后复权尺度计算，输入核的等效成交额=amount×1000×adj_factor；因此核内amount/volume=(amount×1000)/(vol×100)×adj_factor。"
    INPUTS = INPUTS
    SPEC = SPEC
