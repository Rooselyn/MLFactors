"""ChinaAShareEquityCharacteristics（A股特征）

公式：op_q/at_q；符号物理映射：op=operate_profit, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：opa（Operating Profits to Assets）；追踪：PF02017；[来源](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/ed1935598f8ae9ec4588fbe066e5e08d683c652c/char_list.csv)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'operate_profit': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'operate_profit', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'ashare_operating_profit_assets_pit_1q', 'engine': 'financial', 'expression': 'v0/v1', 'leaves': {'v0': ['financial_income', 'operate_profit', 'Q', 0], 'v1': ['financial_balance_sheet', 'total_assets', 'B', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('ashare_operating_profit_assets_pit_1q', {})
class Factor_ashare_operating_profit_assets_pit_1q(PublicFactor):
    name = 'ashare_operating_profit_assets_pit_1q'
    description = 'op_q/at_q；符号物理映射：op=operate_profit, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：opa（Operating Profits to Assets）；追踪：PF02017；[来源](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/ed1935598f8ae9ec4588fbe066e5e08d683c652c/char_list.csv)。'
    INPUTS = INPUTS
    SPEC = SPEC
