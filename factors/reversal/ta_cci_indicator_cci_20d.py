"""Python ta（bukosabino）

公式：TP=(H+L+C)/3；(TP−mean(TP,n))/(0.015×mean(abs(TP−mean(TP,n)),n))；n=20；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：CCIIndicator.cci（window=20, constant=0.015）；追踪：PF00923；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:CCI（period=20, constant=0.015）、bta-lib:cci.cci（period=20, factor=0.015）
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'ta_cci_indicator_cci_20d', 'engine': 'ta', 'module': 'trend', 'class': 'CCIIndicator', 'getter': 'cci', 'parameters': {}, 'minimum': 1}

@register_factor
@fixed_factor('ta_cci_indicator_cci_20d', {})
class Factor_ta_cci_indicator_cci_20d(PublicFactor):
    name = 'ta_cci_indicator_cci_20d'
    description = 'TP=(H+L+C)/3；(TP−mean(TP,n))/(0.015×mean(abs(TP−mean(TP,n)),n))；n=20；数学定义合并；原来源初始化/边界实现仍须按统一缺失口径处理；原目录：CCIIndicator.cci（window=20, constant=0.015）；追踪：PF00923；[来源](https://github.com/bukosabino/ta)。；同定义来源别名：FinTA:CCI（period=20, constant=0.015）、bta-lib:cci.cci（period=20, factor=0.015）'
    INPUTS = INPUTS
    SPEC = SPEC
