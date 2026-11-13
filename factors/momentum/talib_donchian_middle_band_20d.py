"""TA-Lib（技术指标及K线形态）

公式：(max(H,n)+min(L,n))/2；n=20；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：DONCHIAN.outRealMiddleBand（Time Period=20）；追踪：PF00748；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:DonchianChannel.donchian_channel_mband（window=20, offset=0）、Pandas TA Classic:donchian（lower_length=None, upper_length=None）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_donchian_middle_band_20d', 'root_function': 'TA_DONCHIAN', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Time Period': 20.0}, 'options': [20.0], 'outputs': ['outRealUpperBand', 'outRealMiddleBand', 'outRealLowerBand'], 'output_index': 1, 'output_label': 'outRealMiddleBand', 'warmup': 19, 'kernel': 'kernel_9a1af0e76045253e', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInTimePeriod', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outRealUpperBand', 'double'], ['outRealMiddleBand', 'double'], ['outRealLowerBand', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_donchian_middle_band_20d', {})
class Factor_talib_donchian_middle_band_20d(PublicFactor):
    name = 'talib_donchian_middle_band_20d'
    description = "(max(H,n)+min(L,n))/2；n=20；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；默认参数={'Time Period': 20.0}；完整数值核及辅助调用在实现附录展开。；原目录：DONCHIAN.outRealMiddleBand（Time Period=20）；追踪：PF00748；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Python ta（bukosabino）:DonchianChannel.donchian_channel_mband（window=20, offset=0）、Pandas TA Classic:donchian（lower_length=None, upper_length=None）"
    INPUTS = INPUTS
    SPEC = SPEC
