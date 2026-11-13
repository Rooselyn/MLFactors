"""TA-Lib（技术指标及K线形态）

公式：WMA(ROC(C,n1)+ROC(C,n2),wma_n)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_COPPOCK.c)；默认参数={'WMA Period': 10.0, 'ROC-1 Period': 11.0, 'ROC-2 Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：COPPOCK.outReal（WMA Period=10, ROC-1 Period=11, ROC-2 Period=14）；追踪：PF00741；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:coppock（length=10, fast=11, slow=14）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_coppock_outreal_10_11_14d', 'root_function': 'TA_COPPOCK', 'required_inputs': ['inReal'], 'parameters': {'WMA Period': 10.0, 'ROC-1 Period': 11.0, 'ROC-2 Period': 14.0}, 'options': [10.0, 11.0, 14.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 23, 'kernel': 'kernel_19b0c66358c63e7f', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inReal', 'double'], ['optInWMAPeriod', 'int'], ['optInROC1Period', 'int'], ['optInROC2Period', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_coppock_outreal_10_11_14d', {})
class Factor_talib_coppock_outreal_10_11_14d(PublicFactor):
    name = 'talib_coppock_outreal_10_11_14d'
    description = "WMA(ROC(C,n1)+ROC(C,n2),wma_n)；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_COPPOCK.c)；默认参数={'WMA Period': 10.0, 'ROC-1 Period': 11.0, 'ROC-2 Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：COPPOCK.outReal（WMA Period=10, ROC-1 Period=11, ROC-2 Period=14）；追踪：PF00741；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:coppock（length=10, fast=11, slow=14）"
    INPUTS = INPUTS
    SPEC = SPEC
