"""通联 DataYes／优矿424因子库

公式：(T(revenue,q)/T(revenue,q−20))^(1/5)−1；两端TTM均须>0，否则NaN。；原目录：OperatingRevenueGrowRate5Y；追踪：DY0349；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_operatingrevenuegrowrate5y_local_5y', 'engine': 'financial', 'expression': '(positive(v0)/positive(v1))**(1/5)-1', 'leaves': {'v0': ['financial_income', 'revenue', 'T', 0], 'v1': ['financial_income', 'revenue', 'T', 20]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_operatingrevenuegrowrate5y_local_5y', {})
class Factor_datayes_operatingrevenuegrowrate5y_local_5y(PublicFactor):
    name = 'datayes_operatingrevenuegrowrate5y_local_5y'
    description = '(T(revenue,q)/T(revenue,q−20))^(1/5)−1；两端TTM均须>0，否则NaN。；原目录：OperatingRevenueGrowRate5Y；追踪：DY0349；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
