"""通联 DataYes／优矿424因子库

公式：TTM(n_cashflow_act)，最近四个完整报告季度累计金额（元）。；原目录：NetOperateCFTTM；追踪：DY0376；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_net_operatecfttm_pit_4q', 'engine': 'financial', 'expression': 'v0', 'leaves': {'v0': ['financial_cash_flow', 'n_cashflow_act', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_net_operatecfttm_pit_4q', {})
class Factor_datayes_net_operatecfttm_pit_4q(PublicFactor):
    name = 'datayes_net_operatecfttm_pit_4q'
    description = 'TTM(n_cashflow_act)，最近四个完整报告季度累计金额（元）。；原目录：NetOperateCFTTM；追踪：DY0376；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
