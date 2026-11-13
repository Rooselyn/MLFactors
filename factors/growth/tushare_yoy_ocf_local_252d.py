"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：先构造PIT日频X=T(n_cashflow_act)；G=X_t/X_(t−252个交易日)−1；返回当日有效成员平均并列秩/人数。；原目录：yoy_ocf；追踪：PF02520；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'tushare_yoy_ocf_local_252d', 'engine': 'financial', 'expression': 'v0', 'leaves': {'v0': ['financial_cash_flow', 'n_cashflow_act', 'T', 0]}, 'annual': False, 'daily_lag': 252, 'rank': True}

@register_factor
@fixed_factor('tushare_yoy_ocf_local_252d', {})
class Factor_tushare_yoy_ocf_local_252d(PublicFactor):
    name = 'tushare_yoy_ocf_local_252d'
    description = '先构造PIT日频X=T(n_cashflow_act)；G=X_t/X_(t−252个交易日)−1；返回当日有效成员平均并列秩/人数。；原目录：yoy_ocf；追踪：PF02520；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
