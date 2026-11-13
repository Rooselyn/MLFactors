"""ChinaAShareEquityCharacteristics（A股特征）

公式：(sale_q/sale_{q−4}−1)−(invt_q/invt_{q−4}−1)；符号物理映射：sale=revenue, invt=inventories；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：dsi（% Change in Sales minus % Change in Inventory）；追踪：PF02063；[来源](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/ed1935598f8ae9ec4588fbe066e5e08d683c652c/char_list.csv)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'inventories': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'inventories', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'ashare_sales_growth_minus_inventory_growth_pit_4q', 'engine': 'financial', 'expression': '(v0/v1-1)-(v2/v3-1)', 'leaves': {'v0': ['financial_income', 'revenue', 'Q', 0], 'v1': ['financial_income', 'revenue', 'Q', 4], 'v2': ['financial_balance_sheet', 'inventories', 'B', 0], 'v3': ['financial_balance_sheet', 'inventories', 'B', 4]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('ashare_sales_growth_minus_inventory_growth_pit_4q', {})
class Factor_ashare_sales_growth_minus_inventory_growth_pit_4q(PublicFactor):
    name = 'ashare_sales_growth_minus_inventory_growth_pit_4q'
    description = '(sale_q/sale_{q−4}−1)−(invt_q/invt_{q−4}−1)；符号物理映射：sale=revenue, invt=inventories；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：dsi（% Change in Sales minus % Change in Inventory）；追踪：PF02063；[来源](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/ed1935598f8ae9ec4588fbe066e5e08d683c652c/char_list.csv)。'
    INPUTS = INPUTS
    SPEC = SPEC
