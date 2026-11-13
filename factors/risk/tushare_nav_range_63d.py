"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：max(C,63)/min(C,63)；C为同一复权口径，净值起点尺度相消；原目录：high_low_63d；追踪：PF02657；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tushare_nav_range_63d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_nav_range_63d', {})
class Factor_tushare_nav_range_63d(PublicFactor):
    name = 'tushare_nav_range_63d'
    description = 'max(C,63)/min(C,63)；C为同一复权口径，净值起点尺度相消；原目录：high_low_63d；追踪：PF02657；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
