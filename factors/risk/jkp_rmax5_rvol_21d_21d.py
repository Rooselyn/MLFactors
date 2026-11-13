"""JKP Global Factor Data（Jensen–Kelly–Pedersen）

公式：mean(21日内最大的5个日简单收益)/std(R,21,ddof=1)；原目录：rmax5_rvol_21d（Highest 5 days of return scaled by volatility）；追踪：PF01859；[来源](https://github.com/bkelly-lab/ReplicationCrisis/blob/67174c7f170bf8b952b3c86876f187fd9970b5ba/GlobalFactors/Factor%20Details.xlsx)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'jkp_rmax5_rvol_21d_21d', 'engine': 'market'}

@register_factor
@fixed_factor('jkp_rmax5_rvol_21d_21d', {})
class Factor_jkp_rmax5_rvol_21d_21d(PublicFactor):
    name = 'jkp_rmax5_rvol_21d_21d'
    description = 'mean(21日内最大的5个日简单收益)/std(R,21,ddof=1)；原目录：rmax5_rvol_21d（Highest 5 days of return scaled by volatility）；追踪：PF01859；[来源](https://github.com/bkelly-lab/ReplicationCrisis/blob/67174c7f170bf8b952b3c86876f187fd9970b5ba/GlobalFactors/Factor%20Details.xlsx)。'
    INPUTS = INPUTS
    SPEC = SPEC
