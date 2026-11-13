"""bta-lib

公式：x=1,…,14；b=Cov(x,C)/Var(x)，a=mean(C)−bmean(x)；输出a；原目录：linearreg_intercept.intercept（period=14）；追踪：PF01365；[来源](https://github.com/mementum/bta-lib)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'btalib_linearreg_intercept_x1_14d', 'engine': 'explicit', 'period': 14}

@register_factor
@fixed_factor('btalib_linearreg_intercept_x1_14d', {})
class Factor_btalib_linearreg_intercept_x1_14d(PublicFactor):
    name = 'btalib_linearreg_intercept_x1_14d'
    description = 'x=1,…,14；b=Cov(x,C)/Var(x)，a=mean(C)−bmean(x)；输出a；原目录：linearreg_intercept.intercept（period=14）；追踪：PF01365；[来源](https://github.com/mementum/bta-lib)。'
    INPUTS = INPUTS
    SPEC = SPEC
