"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：−log(float_share×10000×close/10^6)；原目录：float_size；追踪：PF02674；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'float_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'float_share'),
    'close': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close'),
}
SPEC = {'name': 'tushare_negative_log_float_cap_million_1d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_negative_log_float_cap_million_1d', {})
class Factor_tushare_negative_log_float_cap_million_1d(PublicFactor):
    name = 'tushare_negative_log_float_cap_million_1d'
    description = '−log(float_share×10000×close/10^6)；原目录：float_size；追踪：PF02674；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
