"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：max(C,126)/min(C,126)；C为同一复权口径，净值起点尺度相消；原目录：high_low_126d；追踪：PF02660；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tushare_nav_range_126d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_nav_range_126d', {})
class Factor_tushare_nav_range_126d(PublicFactor):
    name = 'tushare_nav_range_126d'
    description = 'max(C,126)/min(C,126)；C为同一复权口径，净值起点尺度相消；原目录：high_low_126d；追踪：PF02660；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
