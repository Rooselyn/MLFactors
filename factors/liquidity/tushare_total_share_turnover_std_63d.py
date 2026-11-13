"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：T=V/(total_share×10000)，V以股计；std(T,63)，ddof=1；原目录：std_turnover_63d；追踪：PF02551；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'total_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_share'),
}
SPEC = {'name': 'tushare_total_share_turnover_std_63d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_total_share_turnover_std_63d', {})
class Factor_tushare_total_share_turnover_std_63d(PublicFactor):
    name = 'tushare_total_share_turnover_std_63d'
    description = 'T=V/(total_share×10000)，V以股计；std(T,63)，ddof=1；原目录：std_turnover_63d；追踪：PF02551；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
