"""波幅归一趋势柱·承接确认·当日横截面。

公式：B=Q(div(macd_hfq,atr_hfq)); R=(1+sign(B)*Q(T60(net_elg_amount_dc)-T60(net_md_amount_dc)))/2; X=B*(0.5+R); F=X
类别：动量。业务字段：atr_hfq, macd_hfq, net_elg_amount_dc, net_md_amount_dc。
趋势柱用同复权真实波幅归一，区分趋势推动与单纯高波动带来的大柱值。再以东方财富超大中单差判断同向确认：大额需求相对中等订单更强时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为东方财富超大中单差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'atr_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'atr_hfq'), 'macd_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'macd_hfq'), 'net_elg_amount_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_elg_amount_dc'), 'net_md_amount_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_amount_dc')}
FORMULA = 'B=Q(div(macd_hfq,atr_hfq)); R=(1+sign(B)*Q(T60(net_elg_amount_dc)-T60(net_md_amount_dc)))/2; X=B*(0.5+R); F=X'

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
@fixed_factor('macd_risk_scaled_confirm_level_1d', {})
class Factor_macd_risk_scaled_confirm_level_1d(BaseFactor):
    name = 'macd_risk_scaled_confirm_level_1d'
    description = '趋势柱用同复权真实波幅归一，区分趋势推动与单纯高波动带来的大柱值。再以东方财富超大中单差判断同向确认：大额需求相对中等订单更强时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为东方财富超大中单差。'
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
            B = cross_section_rank(divide(values['macd_hfq'], values['atr_hfq']).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((time_rank(values['net_elg_amount_dc']) - time_rank(values['net_md_amount_dc'])).where(eligible))) / 2
            X = B * (0.5 + R)
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
