"""国泰君安 Alpha191

公式：MIN(RANK(DECAYLINEAR(((((H+L)/2)+H)-(P+H)),20)),RANK(DECAYLINEAR(CORR(((H+L)/2),MEAN(V,40),3),6)))；原目录：GTJA_Alpha191_077；追踪：PF00175；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_077_47d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'min', [('call', 'rank', [('call', 'decaylinear', [('bin', '-', ('bin', '+', ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('var', 'H')), ('bin', '+', ('var', 'P'), ('var', 'H'))), ('num', 20.0)])]), ('call', 'rank', [('call', 'decaylinear', [('call', 'corr', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('call', 'mean', [('var', 'V'), ('num', 40.0)]), ('num', 3.0)]), ('num', 6.0)])])])}

@register_factor
@fixed_factor('alpha191_077_47d', {})
class Factor_alpha191_077_47d(PublicFactor):
    name = 'alpha191_077_47d'
    description = 'MIN(RANK(DECAYLINEAR(((((H+L)/2)+H)-(P+H)),20)),RANK(DECAYLINEAR(CORR(((H+L)/2),MEAN(V,40),3),6)))；原目录：GTJA_Alpha191_077；追踪：PF00175；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
