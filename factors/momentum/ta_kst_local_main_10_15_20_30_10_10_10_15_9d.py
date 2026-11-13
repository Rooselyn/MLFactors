"""Python ta（bukosabino）

公式：KST=100×(MA10(ROC10)+2MA10(ROC15)+3MA10(ROC20)+4MA15(ROC30))，ROCk=C/C.shift(k)−1；signal=MA9(KST)，diff=KST−signal；所有MA完整窗口，初始移位保持NaN。；原目录：KSTIndicator.kst（roc1=10, roc2=15, roc3=20, roc4=30, window1=10, window2=10, window3=10, window4=15, nsig=9）；追踪：PF00919；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:KST（r1=10, r2=15, r3=20, r4=30）、Pandas TA Classic:kst（signal=9）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_kst_local_main_10_15_20_30_10_10_10_15_9d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'kst', 'output': 0}, 'supplied_parameters': {'kind': 'kst', 'output': 0}, 'output_index': 0, 'output_label': 'main', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('ta_kst_local_main_10_15_20_30_10_10_10_15_9d', {})
class Factor_ta_kst_local_main_10_15_20_30_10_10_10_15_9d(PublicFactor):
    name = 'ta_kst_local_main_10_15_20_30_10_10_10_15_9d'
    description = 'KST=100×(MA10(ROC10)+2MA10(ROC15)+3MA10(ROC20)+4MA15(ROC30))，ROCk=C/C.shift(k)−1；signal=MA9(KST)，diff=KST−signal；所有MA完整窗口，初始移位保持NaN。；原目录：KSTIndicator.kst（roc1=10, roc2=15, roc3=20, roc4=30, window1=10, window2=10, window3=10, window4=15, nsig=9）；追踪：PF00919；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:KST（r1=10, r2=15, r3=20, r4=30）、Pandas TA Classic:kst（signal=9）'
    INPUTS = INPUTS
    SPEC = SPEC
