"""TA-Lib（技术指标及K线形态）

公式：−100(max(H,n)−C)/(max(H,n)−min(L,n))；n=14；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：WILLR.outReal（Time Period=14）；追踪：PF00884；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:WilliamsRIndicator.williams_r（lbp=14）、FinTA:WILLIAMS（period=14）、Pandas TA Classic:willr（length=14）、bta-lib:williamsr.r（period=14）、Stockstats:wr（窗口=14）、Tulip Indicators:WILLR.willr（参数：period）、PyTI:williams_percent_r.williams_percent_r（period等由调用方指定）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_willr_14d', 'root_function': 'TA_WILLR', 'required_inputs': ['inHigh', 'inLow', 'inClose'], 'parameters': {'Time Period': 14.0}, 'options': [14.0], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 13, 'kernel': 'kernel_09fd9474cbc7328a', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_willr_14d', {})
class Factor_talib_willr_14d(PublicFactor):
    name = 'talib_willr_14d'
    description = "−100(max(H,n)−C)/(max(H,n)−min(L,n))；n=14；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 14.0}；完整数值核及辅助调用在实现附录展开。；原目录：WILLR.outReal（Time Period=14）；追踪：PF00884；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:WilliamsRIndicator.williams_r（lbp=14）、FinTA:WILLIAMS（period=14）、Pandas TA Classic:willr（length=14）、bta-lib:williamsr.r（period=14）、Stockstats:wr（窗口=14）、Tulip Indicators:WILLR.willr（参数：period）、PyTI:williams_percent_r.williams_percent_r（period等由调用方指定）"
    INPUTS = INPUTS
    SPEC = SPEC
