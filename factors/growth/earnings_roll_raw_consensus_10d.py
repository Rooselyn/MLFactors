"""滚动盈利相对年报改善·原始机制·方向持续共识。

公式：B=Q(log(div(pe,pe_ttm))); X=B; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：成长。业务字段：pe, pe_ttm。
同日静态与滚动市盈率共享市值分子，两者之比可近似反映滚动盈利相对上一年度盈利的改善，研究业绩更新后的缓慢定价。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。这是盈利变化代理，不把市盈率自身上涨解释为盈利增长。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'pe': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe'), 'pe_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe_ttm')}
FORMULA = 'B=Q(log(div(pe,pe_ttm))); X=B; F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('earnings_roll_raw_consensus_10d', {})
class Factor_earnings_roll_raw_consensus_10d(BaseFactor):
    name = 'earnings_roll_raw_consensus_10d'
    description = '同日静态与滚动市盈率共享市值分子，两者之比可近似反映滚动盈利相对上一年度盈利的改善，研究业绩更新后的缓慢定价。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。这是盈利变化代理，不把市盈率自身上涨解释为盈利增长。'
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
            B = cross_section_rank(np.log(divide(values['pe'], values['pe_ttm']).where(divide(values['pe'], values['pe_ttm']) > 0)).where(eligible))
            X = B
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
