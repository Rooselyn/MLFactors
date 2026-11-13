"""JKP Global Factor Data（Jensen–Kelly–Pedersen）

公式：ocf_y/MC_t；符号物理映射：ocf=n_cashflow_act；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：ocf_me（Operating cash flow-to-market）；追踪：PF01738；[来源](https://github.com/bkelly-lab/ReplicationCrisis/blob/67174c7f170bf8b952b3c86876f187fd9970b5ba/GlobalFactors/Factor%20Details.xlsx)。；同定义来源别名：PyAnomaly:FUNDA.ocf_me
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'),
    'n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'jkp_ocf_me_pit_1y', 'engine': 'financial', 'expression': 'v0/MC', 'leaves': {'v0': ['financial_cash_flow', 'n_cashflow_act', 'Y', 0]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('jkp_ocf_me_pit_1y', {})
class Factor_jkp_ocf_me_pit_1y(PublicFactor):
    name = 'jkp_ocf_me_pit_1y'
    description = 'ocf_y/MC_t；符号物理映射：ocf=n_cashflow_act；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：ocf_me（Operating cash flow-to-market）；追踪：PF01738；[来源](https://github.com/bkelly-lab/ReplicationCrisis/blob/67174c7f170bf8b952b3c86876f187fd9970b5ba/GlobalFactors/Factor%20Details.xlsx)。；同定义来源别名：PyAnomaly:FUNDA.ocf_me'
    INPUTS = INPUTS
    SPEC = SPEC
