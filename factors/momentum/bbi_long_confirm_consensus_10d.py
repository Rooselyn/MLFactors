"""多空均线长锚抬升·承接确认·方向持续共识。

公式：B=Q(log(div(bbi_bfq,ma_bfq_60))); R=(1+sign(B)*Q(net_lg_ratio_ths-net_md_ratio_ths))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：动量。业务字段：bbi_bfq, ma_bfq_60, net_lg_ratio_ths, net_md_ratio_ths。
多周期均衡价格高于长均线表示近期成本系统上移，研究多周期趋势扩散。再以同花顺大中单占比判断同向确认：需求占比向更大订单迁移时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为同花顺大中单占比。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'bbi_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'bbi_bfq'), 'ma_bfq_60': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ma_bfq_60'), 'net_lg_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_ratio_ths'), 'net_md_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_ratio_ths')}
FORMULA = 'B=Q(log(div(bbi_bfq,ma_bfq_60))); R=(1+sign(B)*Q(net_lg_ratio_ths-net_md_ratio_ths))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('bbi_long_confirm_consensus_10d', {})
class Factor_bbi_long_confirm_consensus_10d(BaseFactor):
    name = 'bbi_long_confirm_consensus_10d'
    description = '多周期均衡价格高于长均线表示近期成本系统上移，研究多周期趋势扩散。再以同花顺大中单占比判断同向确认：需求占比向更大订单迁移时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为同花顺大中单占比。'
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
            B = cross_section_rank(np.log(divide(values['bbi_bfq'], values['ma_bfq_60']).where(divide(values['bbi_bfq'], values['ma_bfq_60']) > 0)).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((values['net_lg_ratio_ths'] - values['net_md_ratio_ths']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
