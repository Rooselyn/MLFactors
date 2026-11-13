"""低振幅分红收益·承接确认·近期相对前期扩散。

公式：B=Q(div(dv_ratio/100,1+abs(swing))); R=(1+sign(B)*Q(main_net_inflow_ratio_dc))/2; X=B*(0.5+R); F=Q(M5(X)-L5(M15(X)))
类别：价值。业务字段：dv_ratio, main_net_inflow_ratio_dc, swing。
对高分红同时伴随剧烈日内分歧的股票降低权重，研究分红估值支撑能否在较平稳的交易环境中兑现。再以东方财富主力净占比判断同向确认：较大订单合计呈现更强净需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。振幅仅作为同来源相对分歧强度，不赋予未确认的百分比精度。本行条件维度为东方财富主力净占比。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'dv_ratio': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ratio'), 'main_net_inflow_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'main_net_inflow_ratio_dc'), 'swing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'swing')}
FORMULA = 'B=Q(div(dv_ratio/100,1+abs(swing))); R=(1+sign(B)*Q(main_net_inflow_ratio_dc))/2; X=B*(0.5+R); F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('dividend_swing_confirm_diffusion_20d', {})
class Factor_dividend_swing_confirm_diffusion_20d(BaseFactor):
    name = 'dividend_swing_confirm_diffusion_20d'
    description = '对高分红同时伴随剧烈日内分歧的股票降低权重，研究分红估值支撑能否在较平稳的交易环境中兑现。再以东方财富主力净占比判断同向确认：较大订单合计呈现更强净需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。振幅仅作为同来源相对分歧强度，不赋予未确认的百分比精度。本行条件维度为东方财富主力净占比。'
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
            B = cross_section_rank(divide(values['dv_ratio'] / 100, 1 + abs(values['swing'])).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank(values['main_net_inflow_ratio_dc'].where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
