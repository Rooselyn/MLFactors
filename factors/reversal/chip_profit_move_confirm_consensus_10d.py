"""获利盘成本迁移过热·承接确认·方向持续共识。

公式：B=Q(-(winner_rate-50)/50*log(div(cost_50pct,L1(cost_50pct)))); R=(1+sign(B)*Q(net_md_ratio_dc-net_sm_ratio_dc))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：反转。业务字段：cost_50pct, net_md_ratio_dc, net_sm_ratio_dc, winner_rate。
将获利比例与中位成本上移结合，识别筹码整体抬升且获利盘较多的阶段，研究短期兑现压力。再以东方财富中小单差判断同向确认：中等订单承接超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为东方财富中小单差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_50pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_50pct'), 'net_md_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_ratio_dc'), 'net_sm_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_ratio_dc'), 'winner_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'winner_rate')}
FORMULA = 'B=Q(-(winner_rate-50)/50*log(div(cost_50pct,L1(cost_50pct)))); R=(1+sign(B)*Q(net_md_ratio_dc-net_sm_ratio_dc))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('chip_profit_move_confirm_consensus_10d', {})
class Factor_chip_profit_move_confirm_consensus_10d(BaseFactor):
    name = 'chip_profit_move_confirm_consensus_10d'
    description = '将获利比例与中位成本上移结合，识别筹码整体抬升且获利盘较多的阶段，研究短期兑现压力。再以东方财富中小单差判断同向确认：中等订单承接超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为东方财富中小单差。'
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
            B = cross_section_rank((-(values['winner_rate'] - 50) / 50 * np.log(divide(values['cost_50pct'], values['cost_50pct'].shift(1)).where(divide(values['cost_50pct'], values['cost_50pct'].shift(1)) > 0))).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((values['net_md_ratio_dc'] - values['net_sm_ratio_dc']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
