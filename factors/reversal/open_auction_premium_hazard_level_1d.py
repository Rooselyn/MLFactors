"""开盘竞价成交溢价·供给风险扣减·当日横截面。

公式：B=Q(-log(div(close_opening,vwap_opening))); QH=Q(div(cost_95pct-cost_50pct,cost_50pct)); X=B-0.5*QH; F=X
类别：反转。业务字段：close_opening, cost_50pct, cost_95pct, vwap_opening。
竞价末价格高于该阶段成交均价，反映开盘定价中的临末追价，研究开盘情绪在次日的修正。同时考虑竞价需求受到上方高成本供给制约，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为上层套牢分歧。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_opening'), 'cost_50pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_50pct'), 'cost_95pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_95pct'), 'vwap_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vwap_opening')}
FORMULA = 'B=Q(-log(div(close_opening,vwap_opening))); QH=Q(div(cost_95pct-cost_50pct,cost_50pct)); X=B-0.5*QH; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('open_auction_premium_hazard_level_1d', {})
class Factor_open_auction_premium_hazard_level_1d(BaseFactor):
    name = 'open_auction_premium_hazard_level_1d'
    description = '竞价末价格高于该阶段成交均价，反映开盘定价中的临末追价，研究开盘情绪在次日的修正。同时考虑竞价需求受到上方高成本供给制约，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为上层套牢分歧。'
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
            B = cross_section_rank((-np.log(divide(values['close_opening'], values['vwap_opening']).where(divide(values['close_opening'], values['vwap_opening']) > 0))).where(eligible))
            QH = cross_section_rank(divide(values['cost_95pct'] - values['cost_50pct'], values['cost_50pct']).where(eligible))
            X = B - 0.5 * QH
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
