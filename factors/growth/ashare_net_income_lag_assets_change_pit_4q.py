"""ChinaAShareEquityCharacteristics（A股特征）

公式：ni_q/at_{q−1}−ni_{q−4}/at_{q−5}；符号物理映射：ni=n_income, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：droa（4-quarter Changes in Return on Assets）；追踪：PF02008；[来源](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/ed1935598f8ae9ec4588fbe066e5e08d683c652c/char_list.csv)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'n_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'ashare_net_income_lag_assets_change_pit_4q', 'engine': 'financial', 'expression': 'v0/v1-v2/v3', 'leaves': {'v0': ['financial_income', 'n_income', 'Q', 0], 'v1': ['financial_balance_sheet', 'total_assets', 'B', 1], 'v2': ['financial_income', 'n_income', 'Q', 4], 'v3': ['financial_balance_sheet', 'total_assets', 'B', 5]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('ashare_net_income_lag_assets_change_pit_4q', {})
class Factor_ashare_net_income_lag_assets_change_pit_4q(PublicFactor):
    name = 'ashare_net_income_lag_assets_change_pit_4q'
    description = 'ni_q/at_{q−1}−ni_{q−4}/at_{q−5}；符号物理映射：ni=n_income, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：droa（4-quarter Changes in Return on Assets）；追踪：PF02008；[来源](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/ed1935598f8ae9ec4588fbe066e5e08d683c652c/char_list.csv)。'
    INPUTS = INPUTS
    SPEC = SPEC
