"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：mean(C,20)；原目录：ma_20d；追踪：PF02568；[来源](https://tushare.pro/document/2?doc_id=486)。；同定义来源别名：PyTI:keltner_bands.center_band（period等由调用方指定）、PyTI:moving_average_envelope.center_band（period等由调用方指定）、PyTI:bollinger_bands.middle_bollinger_band（std=2.0）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'tushare_close_mean_20d', 'engine': 'market'}

@register_factor
@fixed_factor('tushare_close_mean_20d', {})
class Factor_tushare_close_mean_20d(PublicFactor):
    name = 'tushare_close_mean_20d'
    description = 'mean(C,20)；原目录：ma_20d；追踪：PF02568；[来源](https://tushare.pro/document/2?doc_id=486)。；同定义来源别名：PyTI:keltner_bands.center_band（period等由调用方指定）、PyTI:moving_average_envelope.center_band（period等由调用方指定）、PyTI:bollinger_bands.middle_bollinger_band（std=2.0）'
    INPUTS = INPUTS
    SPEC = SPEC
