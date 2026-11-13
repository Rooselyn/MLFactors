"""通联 DataYes／优矿424因子库

公式：截至t已公告最新一期资产负债表的total_hldr_eqy_exc_min_int（元）。；原目录：TEAP；追踪：DY0061；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_hldr_eqy_exc_min_int': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_hldr_eqy_exc_min_int', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_teap_pit_1q', 'engine': 'financial', 'expression': 'v0', 'leaves': {'v0': ['financial_balance_sheet', 'total_hldr_eqy_exc_min_int', 'B', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_teap_pit_1q', {})
class Factor_datayes_teap_pit_1q(PublicFactor):
    name = 'datayes_teap_pit_1q'
    description = '截至t已公告最新一期资产负债表的total_hldr_eqy_exc_min_int（元）。；原目录：TEAP；追踪：DY0061；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
