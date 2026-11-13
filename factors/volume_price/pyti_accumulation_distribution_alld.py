"""PyTI

公式：完整数值定义为附录独立函数pyti_accumulation_distribution_accumulation_distribution；固定参数={}；原目录定义：累计[((C−L)−(H−C))/(H−L)×V]；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/accumulation_distribution.py#L5)；原目录：accumulation_distribution.accumulation_distribution（period等由调用方指定）；追踪：PF01400；[来源](https://github.com/kylejusticemagnuson/pyti)。
本地数值修正：有限有效H=L=C时当日资金流贡献为0，AD[0]=0，其余累加顺序不变，真实输入缺失仍切段。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'pyti_accumulation_distribution_alld', 'root_function': 'pyti_accumulation_distribution_accumulation_distribution', 'required_inputs': ['close_data', 'high_data', 'low_data', 'volume'], 'parameters': {}, 'supplied_parameters': {}, 'output_index': 0, 'output_label': 'accumulation_distribution', 'kernel': 'kernel_4f886d0687c4eea6', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_accumulation_distribution_alld', {})
class Factor_pyti_accumulation_distribution_alld(PublicFactor):
    name = 'pyti_accumulation_distribution_alld'
    description = 'PyTI累计资金流，每个连续有效输入段AD[0]=0；其余日累计(((C-L)-(H-C))/(H-L))*V。有限有效H=L=C时该日贡献明确设0；真实缺失切段，不跨缺失回填。'
    INPUTS = INPUTS
    SPEC = SPEC
