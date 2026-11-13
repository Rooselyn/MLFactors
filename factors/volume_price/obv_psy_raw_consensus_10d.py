"""能量潮心理线背离·原始机制·方向持续共识。

公式：B=Q(T60(div(D1(obv_bfq),M20(abs(D1(obv_bfq)))))-T60(psy_bfq)); X=B; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：量价。业务字段：obv_bfq, psy_bfq。
交易量方向变化相对上涨频率更强时，研究成交承接是否先于普遍上涨情绪。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'obv_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'obv_bfq'), 'psy_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'psy_bfq')}
FORMULA = 'B=Q(T60(div(D1(obv_bfq),M20(abs(D1(obv_bfq)))))-T60(psy_bfq)); X=B; F=Q(div(M10(X),0.05+M10(abs(X))))'

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
@fixed_factor('obv_psy_raw_consensus_10d', {})
class Factor_obv_psy_raw_consensus_10d(BaseFactor):
    name = 'obv_psy_raw_consensus_10d'
    description = '交易量方向变化相对上涨频率更强时，研究成交承接是否先于普遍上涨情绪。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。'
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
            B = cross_section_rank((time_rank(divide(values['obv_bfq'].diff(1), abs(values['obv_bfq'].diff(1)).rolling(20, min_periods=1).mean())) - time_rank(values['psy_bfq'])).where(eligible))
            X = B
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
