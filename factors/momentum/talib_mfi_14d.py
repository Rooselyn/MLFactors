"""TA-Lib（技术指标及K线形态）

公式：TP=(H+L+C)/3；P=sum(TP×V×I(ΔTP>0),n)，N=sum(TP×V×I(ΔTP<0),n)；100P/(P+N)；n=14；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：MFI.outReal（Time Period=14）；追踪：PF00814；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:MFIIndicator.money_flow_index（window=14）、FinTA:MFI（period=14）、Pandas TA Classic:mfi（length=14）、bta-lib:mfi.mfi（period=14）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'talib_mfi_14d', 'root_function': 'TA_MFI', 'required_inputs': ['inHigh', 'inLow', 'inClose', 'inVolume'], 'parameters': {'Time Period': 14.0}, 'options': [14.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 14, 'kernel': 'kernel_08532349ab805bd1', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['inVolume', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_mfi_14d', {})
class Factor_talib_mfi_14d(PublicFactor):
    name = 'talib_mfi_14d'
    description = "TP=(H+L+C)/3；P=sum(TP×V×I(ΔTP>0),n)，N=sum(TP×V×I(ΔTP<0),n)；100P/(P+N)；n=14；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：MFI.outReal（Time Period=14）；追踪：PF00814；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:MFIIndicator.money_flow_index（window=14）、FinTA:MFI（period=14）、Pandas TA Classic:mfi（length=14）、bta-lib:mfi.mfi（period=14）"
    INPUTS = INPUTS
    SPEC = SPEC
