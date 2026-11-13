"""开盘竞价价格分歧·供给风险扣减·方向持续共识。

公式：B=Q(-div(high_opening-low_opening,high_opening+low_opening)); QH=Q(div(cost_95pct-cost_50pct,cost_50pct)); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：风险。业务字段：cost_50pct, cost_95pct, high_opening, low_opening。
开盘竞价阶段价格分歧越宽，隔夜意见越不一致，研究低竞价分歧与后续风险的关系。同时考虑竞价需求受到上方高成本供给制约，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为上层套牢分歧。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_50pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_50pct'), 'cost_95pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_95pct'), 'high_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_opening'), 'low_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_opening')}
FORMULA = 'B=Q(-div(high_opening-low_opening,high_opening+low_opening)); QH=Q(div(cost_95pct-cost_50pct,cost_50pct)); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('open_auction_width_hazard_consensus_10d', {})
class Factor_open_auction_width_hazard_consensus_10d(BaseFactor):
    name = 'open_auction_width_hazard_consensus_10d'
    description = '开盘竞价阶段价格分歧越宽，隔夜意见越不一致，研究低竞价分歧与后续风险的关系。同时考虑竞价需求受到上方高成本供给制约，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为上层套牢分歧。'
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
            B = cross_section_rank((-divide(values['high_opening'] - values['low_opening'], values['high_opening'] + values['low_opening'])).where(eligible))
            QH = cross_section_rank(divide(values['cost_95pct'] - values['cost_50pct'], values['cost_50pct']).where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
