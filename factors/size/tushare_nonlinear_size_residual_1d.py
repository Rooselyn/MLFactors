"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：S=−log(total_share×10000×close/10^6)；残差=S³−(a+bS)，每日截面含截距OLS；原目录：nl_size；追踪：PF02675；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_share'),
    'close': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close'),
}
SPEC = {'name': 'tushare_nonlinear_size_residual_1d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_nonlinear_size_residual_1d', {})
class Factor_tushare_nonlinear_size_residual_1d(PublicFactor):
    name = 'tushare_nonlinear_size_residual_1d'
    description = 'S=−log(total_share×10000×close/10^6)；残差=S³−(a+bS)，每日截面含截距OLS；原目录：nl_size；追踪：PF02675；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
