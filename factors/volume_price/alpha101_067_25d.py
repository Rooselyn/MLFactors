"""WorldQuant Alpha101

公式：((rank((H - ts_min(H, 2.14593)))^rank(correlation(IndNeutralize(P, SW1), IndNeutralize(adv20, SW3), 6.02936))) * -1)；原目录：Alpha101_067；追踪：PF00067；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1'),
    'industry_sw_3': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_3'),
}
SPEC = {'name': 'alpha101_067_25d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '^', ('call', 'rank', [('bin', '-', ('var', 'H'), ('call', 'ts_min', [('var', 'H'), ('num', 2.14593)]))]), ('call', 'rank', [('call', 'correlation', [('call', 'indneutralize', [('var', 'P'), ('var', 'SW1')]), ('call', 'indneutralize', [('var', 'adv20'), ('var', 'SW3')]), ('num', 6.02936)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_067_25d', {})
class Factor_alpha101_067_25d(PublicFactor):
    name = 'alpha101_067_25d'
    description = '((rank((H - ts_min(H, 2.14593)))^rank(correlation(IndNeutralize(P, SW1), IndNeutralize(adv20, SW3), 6.02936))) * -1)；原目录：Alpha101_067；追踪：PF00067；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
