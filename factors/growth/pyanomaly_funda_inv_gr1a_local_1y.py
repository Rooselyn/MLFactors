"""PyAnomaly

公式：(B(inventories,y)−B(inventories,y−1))/B(total_assets,y)；固定replicate_jkp=True分支，y只取已公告完整财年。；原目录：FUNDA.inv_gr1a；追踪：PF02082；[来源](https://github.com/chulwoohan/pyanomaly)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'inventories': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'inventories', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'pyanomaly_funda_inv_gr1a_local_1y', 'engine': 'financial', 'expression': '(v0-v1)/v2', 'leaves': {'v0': ['financial_balance_sheet', 'inventories', 'B', 0], 'v1': ['financial_balance_sheet', 'inventories', 'B', 4], 'v2': ['financial_balance_sheet', 'total_assets', 'B', 0]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('pyanomaly_funda_inv_gr1a_local_1y', {})
class Factor_pyanomaly_funda_inv_gr1a_local_1y(PublicFactor):
    name = 'pyanomaly_funda_inv_gr1a_local_1y'
    description = '(B(inventories,y)−B(inventories,y−1))/B(total_assets,y)；固定replicate_jkp=True分支，y只取已公告完整财年。；原目录：FUNDA.inv_gr1a；追踪：PF02082；[来源](https://github.com/chulwoohan/pyanomaly)。'
    INPUTS = INPUTS
    SPEC = SPEC
