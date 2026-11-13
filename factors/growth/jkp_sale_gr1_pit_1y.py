"""JKP Global Factor Data（Jensen–Kelly–Pedersen）

公式：sale_y/sale_{y−1}−1；符号物理映射：sale=revenue；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：sale_gr1（Sales Growth (1 year)）；追踪：PF01735；[来源](https://github.com/bkelly-lab/ReplicationCrisis/blob/67174c7f170bf8b952b3c86876f187fd9970b5ba/GlobalFactors/Factor%20Details.xlsx)。；同定义来源别名：PyAnomaly:FUNDA.sale_gr1
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'jkp_sale_gr1_pit_1y', 'engine': 'financial', 'expression': 'v0 / positive(v1) - 1', 'leaves': {'v0': ['financial_income', 'revenue', 'Y', 0], 'v1': ['financial_income', 'revenue', 'Y', 4]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('jkp_sale_gr1_pit_1y', {})
class Factor_jkp_sale_gr1_pit_1y(PublicFactor):
    name = 'jkp_sale_gr1_pit_1y'
    description = 'sale_y/sale_{y−1}−1；符号物理映射：sale=revenue；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：sale_gr1（Sales Growth (1 year)）；追踪：PF01735；[来源](https://github.com/bkelly-lab/ReplicationCrisis/blob/67174c7f170bf8b952b3c86876f187fd9970b5ba/GlobalFactors/Factor%20Details.xlsx)。；同定义来源别名：PyAnomaly:FUNDA.sale_gr1'
    INPUTS = INPUTS
    SPEC = SPEC
