"""笔换手自由流通供给·原始机制·方向持续共识。

公式：B=Q(T60(avg_turnover)*(1-T60(free_share))); X=B; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：流动性。业务字段：avg_turnover, free_share。
在自由流通供给相对不扩张时观察笔换手活跃度，研究有限可交易筹码的实际周转效率。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'avg_turnover': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'avg_turnover'), 'free_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'free_share')}
FORMULA = 'B=Q(T60(avg_turnover)*(1-T60(free_share))); X=B; F=Q(div(M10(X),0.05+M10(abs(X))))'

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
@fixed_factor('turnover_free_supply_raw_consensus_10d', {})
class Factor_turnover_free_supply_raw_consensus_10d(BaseFactor):
    name = 'turnover_free_supply_raw_consensus_10d'
    description = '在自由流通供给相对不扩张时观察笔换手活跃度，研究有限可交易筹码的实际周转效率。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。'
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
            B = cross_section_rank((time_rank(values['avg_turnover']) * (1 - time_rank(values['free_share']))).where(eligible))
            X = B
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
