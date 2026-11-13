"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：mean(A,20)，A以元计；原目录：amount_ma_20d；追踪：PF02535；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'tushare_amount_mean_20d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_amount_mean_20d', {})
class Factor_tushare_amount_mean_20d(PublicFactor):
    name = 'tushare_amount_mean_20d'
    description = 'mean(A,20)，A以元计；原目录：amount_ma_20d；追踪：PF02535；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
