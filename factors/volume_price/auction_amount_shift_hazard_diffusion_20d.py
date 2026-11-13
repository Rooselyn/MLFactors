"""竞价成交金额尾移·供给风险扣减·近期相对前期扩散。

公式：B=Q(T60(amount_closing)-T60(amount_opening)); QH=Q(div(cost_95pct-cost_50pct,cost_50pct)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))
类别：量价。业务字段：amount_closing, amount_opening, cost_50pct, cost_95pct。
用各自历史异常度比较竞价金额的首尾分布，研究早盘关注能否沉淀为收盘交易需求。同时考虑竞价需求受到上方高成本供给制约，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为上层套牢分歧。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'amount_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount_closing'), 'amount_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount_opening'), 'cost_50pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_50pct'), 'cost_95pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_95pct')}
FORMULA = 'B=Q(T60(amount_closing)-T60(amount_opening)); QH=Q(div(cost_95pct-cost_50pct,cost_50pct)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))'

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
@fixed_factor('auction_amount_shift_hazard_diffusion_20d', {})
class Factor_auction_amount_shift_hazard_diffusion_20d(BaseFactor):
    name = 'auction_amount_shift_hazard_diffusion_20d'
    description = '用各自历史异常度比较竞价金额的首尾分布，研究早盘关注能否沉淀为收盘交易需求。同时考虑竞价需求受到上方高成本供给制约，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为上层套牢分歧。'
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
            B = cross_section_rank((time_rank(values['amount_closing']) - time_rank(values['amount_opening'])).where(eligible))
            QH = cross_section_rank(divide(values['cost_95pct'] - values['cost_50pct'], values['cost_50pct']).where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
