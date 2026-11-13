"""Pandas TA Classic

公式：Corr(C窗口,0,…,n−1)；n=12；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：cti（length=12）；追踪：PF01185；[来源](https://github.com/xgboosted/pandas-ta-classic)。；同定义来源别名：Stockstats:cti（窗口=12）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_cti_12d', 'engine': 'explicit', 'period': 12}

@register_factor
@fixed_factor('ptac_cti_12d', {})
class Factor_ptac_cti_12d(PublicFactor):
    name = 'ptac_cti_12d'
    description = 'Corr(C窗口,0,…,n−1)；n=12；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：cti（length=12）；追踪：PF01185；[来源](https://github.com/xgboosted/pandas-ta-classic)。；同定义来源别名：Stockstats:cti（窗口=12）'
    INPUTS = INPUTS
    SPEC = SPEC
