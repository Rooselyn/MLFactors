"""布林中轨指数锚差·承接确认·方向持续共识。

公式：B=Q(log(div(boll_mid_hfq,ema_hfq_30))); R=(1+sign(B)*Q(main_net_inflow_ratio_dc))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：动量。业务字段：boll_mid_hfq, ema_hfq_30, main_net_inflow_ratio_dc。
不同加权方式的均衡价格出现有向差异时，研究近期价格接受度的变化。再以东方财富主力净占比判断同向确认：较大订单合计呈现更强净需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为东方财富主力净占比。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'boll_mid_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'boll_mid_hfq'), 'ema_hfq_30': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ema_hfq_30'), 'main_net_inflow_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'main_net_inflow_ratio_dc')}
FORMULA = 'B=Q(log(div(boll_mid_hfq,ema_hfq_30))); R=(1+sign(B)*Q(main_net_inflow_ratio_dc))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('boll_ema_anchor_confirm_consensus_10d', {})
class Factor_boll_ema_anchor_confirm_consensus_10d(BaseFactor):
    name = 'boll_ema_anchor_confirm_consensus_10d'
    description = '不同加权方式的均衡价格出现有向差异时，研究近期价格接受度的变化。再以东方财富主力净占比判断同向确认：较大订单合计呈现更强净需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为东方财富主力净占比。'
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
            B = cross_section_rank(np.log(divide(values['boll_mid_hfq'], values['ema_hfq_30']).where(divide(values['boll_mid_hfq'], values['ema_hfq_30']) > 0)).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank(values['main_net_inflow_ratio_dc'].where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
