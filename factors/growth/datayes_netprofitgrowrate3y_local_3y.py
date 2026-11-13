"""通联 DataYes／优矿424因子库

公式：(T(n_income,q)/T(n_income,q−12))^(1/3)−1；两端TTM均须>0，否则NaN。；原目录：NetProfitGrowRate3Y；追踪：DY0344；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'n_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_netprofitgrowrate3y_local_3y', 'engine': 'financial', 'expression': '(positive(v0)/positive(v1))**(1/3)-1', 'leaves': {'v0': ['financial_income', 'n_income', 'T', 0], 'v1': ['financial_income', 'n_income', 'T', 12]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_netprofitgrowrate3y_local_3y', {})
class Factor_datayes_netprofitgrowrate3y_local_3y(PublicFactor):
    name = 'datayes_netprofitgrowrate3y_local_3y'
    description = '(T(n_income,q)/T(n_income,q−12))^(1/3)−1；两端TTM均须>0，否则NaN。；原目录：NetProfitGrowRate3Y；追踪：DY0344；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
