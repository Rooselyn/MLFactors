"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：∏_{j=0…62}(1+R[t−j])−1=C[t]/C[t−63]−1；原目录：return_63d；追踪：PF02572；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tushare_return_63d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_return_63d', {})
class Factor_tushare_return_63d(PublicFactor):
    name = 'tushare_return_63d'
    description = '∏_{j=0…62}(1+R[t−j])−1=C[t]/C[t−63]−1；原目录：return_63d；追踪：PF02572；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
