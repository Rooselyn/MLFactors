"""通联 DataYes／优矿424因子库

公式：T(total_profit)/(T(oper_cost)+T(biz_tax_surchg)+T(sell_exp)+T(admin_exp)+T(fin_exp))；成本费用明确包含营业税金及附加。；原目录：TotalProfitCostRatio；追踪：DY0200；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_profit': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'total_profit', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'oper_cost': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'oper_cost', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'biz_tax_surchg': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'biz_tax_surchg', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'sell_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'sell_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'admin_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'admin_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'fin_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'fin_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_totalprofitcostratio_local_4q', 'engine': 'financial', 'expression': 'v0/(v1+v2+v3+v4+v5)', 'leaves': {'v0': ['financial_income', 'total_profit', 'T', 0], 'v1': ['financial_income', 'oper_cost', 'T', 0], 'v2': ['financial_income', 'biz_tax_surchg', 'T', 0], 'v3': ['financial_income', 'sell_exp', 'T', 0], 'v4': ['financial_income', 'admin_exp', 'T', 0], 'v5': ['financial_income', 'fin_exp', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_totalprofitcostratio_local_4q', {})
class Factor_datayes_totalprofitcostratio_local_4q(PublicFactor):
    name = 'datayes_totalprofitcostratio_local_4q'
    description = 'T(total_profit)/(T(oper_cost)+T(biz_tax_surchg)+T(sell_exp)+T(admin_exp)+T(fin_exp))；成本费用明确包含营业税金及附加。；原目录：TotalProfitCostRatio；追踪：DY0200；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
