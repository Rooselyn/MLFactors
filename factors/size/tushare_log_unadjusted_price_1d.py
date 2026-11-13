"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：log(close)，close>0；原目录：log_price；追踪：PF02673；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close'),
}
SPEC = {'name': 'tushare_log_unadjusted_price_1d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_log_unadjusted_price_1d', {})
class Factor_tushare_log_unadjusted_price_1d(PublicFactor):
    name = 'tushare_log_unadjusted_price_1d'
    description = 'log(close)，close>0；原目录：log_price；追踪：PF02673；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
