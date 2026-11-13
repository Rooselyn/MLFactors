"""筹码中圈收敛·承接确认·保守持续强度。

公式：B=Q(-div(cost_85pct-cost_15pct,cost_85pct+cost_15pct)); R=(1+sign(B)*Q(T60(net_md_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=Q(M20(X)-SD20(X))
类别：风险。业务字段：cost_15pct, cost_85pct, net_md_amount_ths, net_sm_amount_ths。
中间多数筹码成本收敛体现主要交易成本趋同，区别于仅由少量极端价位决定的尾部风险。再以同花顺中小单承接判断同向确认：中等订单需求超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为同花顺中小单承接。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_15pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_15pct'), 'cost_85pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_85pct'), 'net_md_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_amount_ths'), 'net_sm_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_amount_ths')}
FORMULA = 'B=Q(-div(cost_85pct-cost_15pct,cost_85pct+cost_15pct)); R=(1+sign(B)*Q(T60(net_md_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('chip_inner_confirm_lowerbound_20d', {})
class Factor_chip_inner_confirm_lowerbound_20d(BaseFactor):
    name = 'chip_inner_confirm_lowerbound_20d'
    description = '中间多数筹码成本收敛体现主要交易成本趋同，区别于仅由少量极端价位决定的尾部风险。再以同花顺中小单承接判断同向确认：中等订单需求超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为同花顺中小单承接。'
    INPUTS = INPUTS
    FORMULA = FORMULA
    warmup_days = 100
    BOUNDED_HISTORY = True

    def generate_signals(self, data, constituents=None):
        dates = pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values()
        symbols = data.index.get_level_values('symbol').unique().sort_values()
        if data.empty:
            return pd.DataFrame(index=dates, columns=symbols, dtype=float)
        eligible = eligibility(data, dates, symbols)
        values = {field: pd.to_numeric(data[field], errors='coerce').unstack('symbol').reindex(index=dates, columns=symbols).astype(float).replace([np.inf, -np.inf], np.nan) for field in self.INPUTS}
        with np.errstate(all='ignore'):
            B = cross_section_rank((-divide(values['cost_85pct'] - values['cost_15pct'], values['cost_85pct'] + values['cost_15pct'])).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((time_rank(values['net_md_amount_ths']) - time_rank(values['net_sm_amount_ths'])).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
