"""通联 DataYes／优矿424因子库

公式：TTM(c_fr_sale_sg)，最近四个完整报告季度累计金额（元）。；原目录：SaleServiceRenderCashTTM；追踪：DY0386；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'c_fr_sale_sg': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'c_fr_sale_sg', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_sale_service_render_cashttm_pit_4q', 'engine': 'financial', 'expression': 'v0', 'leaves': {'v0': ['financial_cash_flow', 'c_fr_sale_sg', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_sale_service_render_cashttm_pit_4q', {})
class Factor_datayes_sale_service_render_cashttm_pit_4q(PublicFactor):
    name = 'datayes_sale_service_render_cashttm_pit_4q'
    description = 'TTM(c_fr_sale_sg)，最近四个完整报告季度累计金额（元）。；原目录：SaleServiceRenderCashTTM；追踪：DY0386；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
