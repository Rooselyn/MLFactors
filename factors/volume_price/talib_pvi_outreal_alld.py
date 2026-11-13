"""TA-Lib（技术指标及K线形态）

公式：PVI_t=PVI_{t−1}×(1+R_t)若V_t>V_{t−1}，否则保持；初值按来源；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_PVI.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：PVI.outReal（无窗口参数）；追踪：PF00830；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:PVI.pvi（参数：none）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'talib_pvi_outreal_alld', 'root_function': 'TA_PVI', 'required_inputs': ['inClose', 'inVolume'], 'parameters': {}, 'options': [], 'outputs': ['outReal'], 'output_index': 0, 'output_label': 'outReal', 'warmup': 0, 'kernel': 'kernel_41cb1e2403e39211', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inClose', 'double'], ['inVolume', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outReal', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_pvi_outreal_alld', {})
class Factor_talib_pvi_outreal_alld(PublicFactor):
    name = 'talib_pvi_outreal_alld'
    description = 'PVI_t=PVI_{t−1}×(1+R_t)若V_t>V_{t−1}，否则保持；初值按来源；本行取输出outReal。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_PVI.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：PVI.outReal（无窗口参数）；追踪：PF00830；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Tulip Indicators:PVI.pvi（参数：none）'
    INPUTS = INPUTS
    SPEC = SPEC
