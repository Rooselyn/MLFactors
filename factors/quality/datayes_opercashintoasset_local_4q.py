"""通联 DataYes／优矿424因子库

公式：T(n_cashflow_act)/AVG4(total_assets)；AVG4(X)=(B(X,q)+B(X,q−4))/2。；原目录：OperCashInToAsset；追踪：DY0408；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_opercashintoasset_local_4q', 'engine': 'financial', 'expression': 'v0/v1', 'leaves': {'v0': ['financial_cash_flow', 'n_cashflow_act', 'T', 0], 'v1': ['financial_balance_sheet', 'total_assets', 'AVG4', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_opercashintoasset_local_4q', {})
class Factor_datayes_opercashintoasset_local_4q(PublicFactor):
    name = 'datayes_opercashintoasset_local_4q'
    description = 'T(n_cashflow_act)/AVG4(total_assets)；AVG4(X)=(B(X,q)+B(X,q−4))/2。；原目录：OperCashInToAsset；追踪：DY0408；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
