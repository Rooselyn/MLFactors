"""同花顺大小单分化·供给风险扣减·当日横截面。

公式：B=Q(T60(net_lg_amount_ths)-T60(net_sm_amount_ths)); QH=Q(winner_rate); X=B-0.5*QH; F=X
类别：量价。业务字段：net_lg_amount_ths, net_sm_amount_ths, winner_rate。
比较同一来源大单与小单净流入的异常度，研究大额需求能否在小额交易分歧中延续。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为获利兑现供给。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'net_lg_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_amount_ths'), 'net_sm_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_amount_ths'), 'winner_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'winner_rate')}
FORMULA = 'B=Q(T60(net_lg_amount_ths)-T60(net_sm_amount_ths)); QH=Q(winner_rate); X=B-0.5*QH; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('ths_large_small_hazard_level_1d', {})
class Factor_ths_large_small_hazard_level_1d(BaseFactor):
    name = 'ths_large_small_hazard_level_1d'
    description = '比较同一来源大单与小单净流入的异常度，研究大额需求能否在小额交易分歧中延续。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为获利兑现供给。'
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
            B = cross_section_rank((time_rank(values['net_lg_amount_ths']) - time_rank(values['net_sm_amount_ths'])).where(eligible))
            QH = cross_section_rank(values['winner_rate'].where(eligible))
            X = B - 0.5 * QH
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
