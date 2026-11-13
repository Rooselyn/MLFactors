"""尾盘竞价价格分歧·供给风险扣减·近期相对前期扩散。

公式：B=Q(-div(high_closing-low_closing,high_closing+low_closing)); QH=Q(div(cost_95pct-cost_50pct,cost_50pct)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))
类别：风险。业务字段：cost_50pct, cost_95pct, high_closing, low_closing。
尾盘集合定价过程的宽幅变化可能反映收盘争夺，研究较低尾盘分歧是否降低隔夜风险。同时考虑竞价需求受到上方高成本供给制约，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为上层套牢分歧。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_50pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_50pct'), 'cost_95pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_95pct'), 'high_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_closing'), 'low_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_closing')}
FORMULA = 'B=Q(-div(high_closing-low_closing,high_closing+low_closing)); QH=Q(div(cost_95pct-cost_50pct,cost_50pct)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('close_auction_width_hazard_diffusion_20d', {})
class Factor_close_auction_width_hazard_diffusion_20d(BaseFactor):
    name = 'close_auction_width_hazard_diffusion_20d'
    description = '尾盘集合定价过程的宽幅变化可能反映收盘争夺，研究较低尾盘分歧是否降低隔夜风险。同时考虑竞价需求受到上方高成本供给制约，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为上层套牢分歧。'
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
            B = cross_section_rank((-divide(values['high_closing'] - values['low_closing'], values['high_closing'] + values['low_closing'])).where(eligible))
            QH = cross_section_rank(divide(values['cost_95pct'] - values['cost_50pct'], values['cost_50pct']).where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
