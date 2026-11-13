"""JKP Global Factor Data（Jensen–Kelly–Pedersen）

公式：(Y(income_tax,y)−Y(income_tax,y−1))/B(total_assets,y−1)，Y只取已公告12月31日完整年报。；原目录：tax_gr1a；追踪：PF01720；[来源](https://github.com/bkelly-lab/ReplicationCrisis/blob/67174c7f170bf8b952b3c86876f187fd9970b5ba/GlobalFactors/Factor%20Details.xlsx)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'income_tax': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'income_tax', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'jkp_tax_gr1a_local_1y', 'engine': 'financial', 'expression': '(v0-v1)/v2', 'leaves': {'v0': ['financial_income', 'income_tax', 'Y', 0], 'v1': ['financial_income', 'income_tax', 'Y', 4], 'v2': ['financial_balance_sheet', 'total_assets', 'B', 4]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('jkp_tax_gr1a_local_1y', {})
class Factor_jkp_tax_gr1a_local_1y(PublicFactor):
    name = 'jkp_tax_gr1a_local_1y'
    description = '(Y(income_tax,y)−Y(income_tax,y−1))/B(total_assets,y−1)，Y只取已公告12月31日完整年报。；原目录：tax_gr1a；追踪：PF01720；[来源](https://github.com/bkelly-lab/ReplicationCrisis/blob/67174c7f170bf8b952b3c86876f187fd9970b5ba/GlobalFactors/Factor%20Details.xlsx)。'
    INPUTS = INPUTS
    SPEC = SPEC
