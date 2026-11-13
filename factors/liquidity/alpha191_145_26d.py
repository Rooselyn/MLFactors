"""国泰君安 Alpha191

公式：(MEAN(V,9)-MEAN(V,26))/MEAN(V,12)*100；原目录：GTJA_Alpha191_145；追踪：PF00239；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_145_26d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('bin', '-', ('call', 'mean', [('var', 'V'), ('num', 9.0)]), ('call', 'mean', [('var', 'V'), ('num', 26.0)])), ('call', 'mean', [('var', 'V'), ('num', 12.0)])), ('num', 100.0))}

@register_factor
@fixed_factor('alpha191_145_26d', {})
class Factor_alpha191_145_26d(PublicFactor):
    name = 'alpha191_145_26d'
    description = '(MEAN(V,9)-MEAN(V,26))/MEAN(V,12)*100；原目录：GTJA_Alpha191_145；追踪：PF00239；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
