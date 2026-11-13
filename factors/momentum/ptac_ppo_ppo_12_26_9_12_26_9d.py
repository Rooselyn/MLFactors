"""Pandas TA Classic

公式：100×(MA(C,fast)−MA(C,slow))/MA(C,slow)；Signal=EMA(PPO,signal)；Hist=PPO−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/ppo.py#L48)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'scalar': 100, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'PPO_12_26_9'；原目录：ppo（fast=12, slow=26, signal=9, scalar=100, mamode='sma'）；追踪：PF01199；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_ppo_ppo_12_26_9_12_26_9d', 'root_function': 'f_a7de0f2567_ppo', 'required_inputs': ['close'], 'parameters': {'fast': 12, 'slow': 26, 'signal': 9, 'scalar': 100, 'mamode': 'sma', 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PPO_12_26_9', 'gate_bars': 1, 'kernel': 'kernel_f0476954baed4110', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_ppo_ppo_12_26_9_12_26_9d', {})
class Factor_ptac_ppo_ppo_12_26_9_12_26_9d(PublicFactor):
    name = 'ptac_ppo_ppo_12_26_9_12_26_9d'
    description = "100×(MA(C,fast)−MA(C,slow))/MA(C,slow)；Signal=EMA(PPO,signal)；Hist=PPO−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/ppo.py#L48)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'scalar': 100, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'PPO_12_26_9'；原目录：ppo（fast=12, slow=26, signal=9, scalar=100, mamode='sma'）；追踪：PF01199；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
