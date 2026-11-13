"""筹码外圈收敛·承接确认·当日横截面。

公式：B=Q(-div(cost_95pct-cost_5pct,cost_95pct+cost_5pct)); R=(1+sign(B)*Q(T60(net_lg_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=X
类别：风险。业务字段：cost_5pct, cost_95pct, net_lg_amount_ths, net_sm_amount_ths。
外圈成本跨度越小，潜在持仓盈亏分歧越集中，研究低筹码分歧能否降低急跌时的供给不确定性。再以同花顺大小单承接判断同向确认：较大订单相对小单有更强的边际需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为同花顺大小单承接。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_5pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_5pct'), 'cost_95pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_95pct'), 'net_lg_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_amount_ths'), 'net_sm_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_amount_ths')}
FORMULA = 'B=Q(-div(cost_95pct-cost_5pct,cost_95pct+cost_5pct)); R=(1+sign(B)*Q(T60(net_lg_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=X'

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
@fixed_factor('chip_outer_confirm_level_1d', {})
class Factor_chip_outer_confirm_level_1d(BaseFactor):
    name = 'chip_outer_confirm_level_1d'
    description = '外圈成本跨度越小，潜在持仓盈亏分歧越集中，研究低筹码分歧能否降低急跌时的供给不确定性。再以同花顺大小单承接判断同向确认：较大订单相对小单有更强的边际需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为同花顺大小单承接。'
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
            B = cross_section_rank((-divide(values['cost_95pct'] - values['cost_5pct'], values['cost_95pct'] + values['cost_5pct'])).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((time_rank(values['net_lg_amount_ths']) - time_rank(values['net_sm_amount_ths'])).where(eligible))) / 2
            X = B * (0.5 + R)
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
