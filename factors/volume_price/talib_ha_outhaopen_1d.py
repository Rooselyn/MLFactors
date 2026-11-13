"""TA-Lib（技术指标及K线形态）

公式：HA_close=(O+H+L+C)/4；HA_open=(前HA_open+前HA_close)/2；HA_high=max(H,HA_open,HA_close)，HA_low=min(L,HA_open,HA_close)；本行取输出outHAOpen。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_HA.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：HA.outHAOpen（无窗口参数）；追踪：PF00765；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:ha（原函数默认参数/显式周期）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'talib_ha_outhaopen_1d', 'root_function': 'TA_HA', 'required_inputs': ['inOpen', 'inHigh', 'inLow', 'inClose'], 'parameters': {}, 'options': [], 'outputs': ['outHAOpen', 'outHAHigh', 'outHALow', 'outHAClose'], 'output_index': 0, 'output_label': 'outHAOpen', 'warmup': 0, 'kernel': 'kernel_2f12db42812d2380', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inOpen', 'double'], ['inHigh', 'double'], ['inLow', 'double'], ['inClose', 'double'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outHAOpen', 'double'], ['outHAHigh', 'double'], ['outHALow', 'double'], ['outHAClose', 'double']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_ha_outhaopen_1d', {})
class Factor_talib_ha_outhaopen_1d(PublicFactor):
    name = 'talib_ha_outhaopen_1d'
    description = 'HA_close=(O+H+L+C)/4；HA_open=(前HA_open+前HA_close)/2；HA_high=max(H,HA_open,HA_close)，HA_low=min(L,HA_open,HA_close)；本行取输出outHAOpen。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_HA.c)；默认参数={}；完整数值核及辅助调用在实现附录展开。；原目录：HA.outHAOpen（无窗口参数）；追踪：PF00765；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。；同定义来源别名：Pandas TA Classic:ha（原函数默认参数/显式周期）'
    INPUTS = INPUTS
    SPEC = SPEC
