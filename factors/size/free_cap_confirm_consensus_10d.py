"""开盘自由流通市值·承接确认·方向持续共识。

公式：B=Q(-log(10000*free_share*open)); R=(1+sign(B)*Q(T60(net_elg_amount_dc)-T60(net_md_amount_dc)))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：规模。业务字段：free_share, net_elg_amount_dc, net_md_amount_dc, open。
以自由流通股本乘开盘价衡量可交易市值，研究A股交易供给较小股票的规模溢价及其容量约束。再以东方财富超大中单差判断同向确认：大额需求相对中等订单更强时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。这是开盘口径自由流通市值，不冒充收盘总市值。本行条件维度为东方财富超大中单差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'free_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'free_share'), 'net_elg_amount_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_elg_amount_dc'), 'net_md_amount_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_amount_dc'), 'open': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open')}
FORMULA = 'B=Q(-log(10000*free_share*open)); R=(1+sign(B)*Q(T60(net_elg_amount_dc)-T60(net_md_amount_dc)))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))'

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
@fixed_factor('free_cap_confirm_consensus_10d', {})
class Factor_free_cap_confirm_consensus_10d(BaseFactor):
    name = 'free_cap_confirm_consensus_10d'
    description = '以自由流通股本乘开盘价衡量可交易市值，研究A股交易供给较小股票的规模溢价及其容量约束。再以东方财富超大中单差判断同向确认：大额需求相对中等订单更强时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。这是开盘口径自由流通市值，不冒充收盘总市值。本行条件维度为东方财富超大中单差。'
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
            B = cross_section_rank((-np.log((10000 * values['free_share'] * values['open']).where(10000 * values['free_share'] * values['open'] > 0))).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((time_rank(values['net_elg_amount_dc']) - time_rank(values['net_md_amount_dc'])).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
