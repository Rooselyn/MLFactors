"""通联 DataYes／优矿424因子库

公式：B(fix_assets_total)，最新报告固定资产合计（元）；不以该项冒充美国PP&E。；原目录：TotalFixedAssets；追踪：DY0391；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'fix_assets_total': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'fix_assets_total', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_totalfixedassets_local_1q', 'engine': 'financial', 'expression': 'v0', 'leaves': {'v0': ['financial_balance_sheet', 'fix_assets_total', 'B', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_totalfixedassets_local_1q', {})
class Factor_datayes_totalfixedassets_local_1q(PublicFactor):
    name = 'datayes_totalfixedassets_local_1q'
    description = 'B(fix_assets_total)，最新报告固定资产合计（元）；不以该项冒充美国PP&E。；原目录：TotalFixedAssets；追踪：DY0391；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
