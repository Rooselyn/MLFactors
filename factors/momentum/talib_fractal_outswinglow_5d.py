"""TA-Lib（技术指标及K线形态）

公式：源码核心递推表达式（完整分支/参数见链接）：for( i = optInLeftBars + optInRightBars; i >= 0; i -= 1 )；} else if( i == optInLeftBars + optInRightBars )；outIdx += 1;；today += 1;；for( i = sp->optInLeftBars + sp->optInRightBars; i >= 0; i -= 1 )；tempHigh = sp->win_i_inHigh[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；tempLow = sp->win_i_inLow[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；} else if( i == sp->optInLeftBars + sp->optInRightBars )；sp->cur_outSwingHigh = *outSwingHigh;；sp->cur_outSwingLow = *outSwingLow;；sp->winPos_i = sp->winPos_i + 1;；sp = (struct TA_FRACTAL_Stream *)TA_Malloc( sizeof(*sp) );；sp->winCap_i = (int)(optInLeftBars + optInRightBars + 1);；sp->win_i_inHigh = (double *)TA_Malloc( sizeof(double) * (size_t)sp->winCap_i );；本行取输出outSwingLow。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_FRACTAL.c)；默认参数={'Left Bars': 2.0, 'Right Bars': 2.0}；完整数值核及辅助调用在实现附录展开。；原目录：FRACTAL.outSwingLow（Left Bars=2, Right Bars=2）；追踪：PF00763；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'talib_fractal_outswinglow_5d', 'root_function': 'TA_FRACTAL', 'required_inputs': ['inHigh', 'inLow'], 'parameters': {'Left Bars': 2.0, 'Right Bars': 2.0}, 'options': [2.0, 2.0], 'outputs': ['outSwingHigh', 'outSwingLow'], 'output_index': 1, 'output_label': 'outSwingLow', 'warmup': 4, 'kernel': 'kernel_52b4c3c6fa03d27e', 'engine': 'talib', 'abi': [['startIdx', 'int'], ['endIdx', 'int'], ['inHigh', 'double'], ['inLow', 'double'], ['optInLeftBars', 'int'], ['optInRightBars', 'int'], ['outBegIdx', 'int'], ['outNBElement', 'int'], ['outSwingHigh', 'int'], ['outSwingLow', 'int']], 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('talib_fractal_outswinglow_5d', {})
class Factor_talib_fractal_outswinglow_5d(PublicFactor):
    name = 'talib_fractal_outswinglow_5d'
    description = "源码核心递推表达式（完整分支/参数见链接）：for( i = optInLeftBars + optInRightBars; i >= 0; i -= 1 )；} else if( i == optInLeftBars + optInRightBars )；outIdx += 1;；today += 1;；for( i = sp->optInLeftBars + sp->optInRightBars; i >= 0; i -= 1 )；tempHigh = sp->win_i_inHigh[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；tempLow = sp->win_i_inLow[(sp->winPos_i + sp->winCap_i - i >= sp->winCap_i) ? sp->winPos_i + sp->winCap_i - i - sp->winCap_i : sp->winPos_i + sp->winCap_i - i];；} else if( i == sp->optInLeftBars + sp->optInRightBars )；sp->cur_outSwingHigh = *outSwingHigh;；sp->cur_outSwingLow = *outSwingLow;；sp->winPos_i = sp->winPos_i + 1;；sp = (struct TA_FRACTAL_Stream *)TA_Malloc( sizeof(*sp) );；sp->winCap_i = (int)(optInLeftBars + optInRightBars + 1);；sp->win_i_inHigh = (double *)TA_Malloc( sizeof(double) * (size_t)sp->winCap_i );；本行取输出outSwingLow。[算法源码](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/src/ta_func/ta_FRACTAL.c)；默认参数={'Left Bars': 2.0, 'Right Bars': 2.0}；完整数值核及辅助调用在实现附录展开。；原目录：FRACTAL.outSwingLow（Left Bars=2, Right Bars=2）；追踪：PF00763；[来源](https://github.com/TA-Lib/ta-lib/blob/481dda1b10350468e82221b17fe84f6bb24e122d/ta_func_api.xml)。"
    INPUTS = INPUTS
    SPEC = SPEC
