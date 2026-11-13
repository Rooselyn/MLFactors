"""PyAnomaly

公式：S=Σ_{j=0…4}r[m−(71+12j)]；(Σ_{k=60…119}r[m−k]−S)/(11×5)；原目录：CRSPM.seas_6_10na；追踪：PF02237；[来源](https://github.com/chulwoohan/pyanomaly)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyanomaly_crspm_seas_6_10na_10y', 'engine': 'market'}

@register_factor
@fixed_factor('pyanomaly_crspm_seas_6_10na_10y', {})
class Factor_pyanomaly_crspm_seas_6_10na_10y(PublicFactor):
    name = 'pyanomaly_crspm_seas_6_10na_10y'
    description = 'S=Σ_{j=0…4}r[m−(71+12j)]；(Σ_{k=60…119}r[m−k]−S)/(11×5)；原目录：CRSPM.seas_6_10na；追踪：PF02237；[来源](https://github.com/chulwoohan/pyanomaly)。'
    INPUTS = INPUTS
    SPEC = SPEC
