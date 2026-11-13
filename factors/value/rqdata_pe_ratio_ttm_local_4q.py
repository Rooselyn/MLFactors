"""RQData／米筐因子库（公开文档核实选集）

公式：MC/T(n_income_attr_p)，TTM利润≤0为NaN。；原目录：pe_ratio_ttm；追踪：PF02689；[来源](https://www.ricequant.com/doc/rqdata/python/stock-mod.html)。；同定义来源别名：通联 DataYes／优矿424因子库:PE
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'),
    'n_income_attr_p': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income_attr_p', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'rqdata_pe_ratio_ttm_local_4q', 'engine': 'financial', 'expression': 'MC / positive(v0)', 'leaves': {'v0': ['financial_income', 'n_income_attr_p', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('rqdata_pe_ratio_ttm_local_4q', {})
class Factor_rqdata_pe_ratio_ttm_local_4q(PublicFactor):
    name = 'rqdata_pe_ratio_ttm_local_4q'
    description = 'MC/T(n_income_attr_p)，TTM利润≤0为NaN。；原目录：pe_ratio_ttm；追踪：PF02689；[来源](https://www.ricequant.com/doc/rqdata/python/stock-mod.html)。；同定义来源别名：通联 DataYes／优矿424因子库:PE'
    INPUTS = INPUTS
    SPEC = SPEC
