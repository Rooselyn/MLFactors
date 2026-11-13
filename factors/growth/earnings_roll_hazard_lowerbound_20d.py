"""滚动盈利相对年报改善·供给风险扣减·保守持续强度。

公式：B=Q(log(div(pe,pe_ttm))); QH=Q(turnover_rate_f); X=B-0.5*QH; F=Q(M20(X)-SD20(X))
类别：成长。业务字段：pe, pe_ttm, turnover_rate_f。
同日静态与滚动市盈率共享市值分子，两者之比可近似反映滚动盈利相对上一年度盈利的改善，研究业绩更新后的缓慢定价。同时考虑估值或报表信号受到过热交易关注挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。这是盈利变化代理，不把市盈率自身上涨解释为盈利增长。本行条件维度为换手关注拥挤。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'pe': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe'), 'pe_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe_ttm'), 'turnover_rate_f': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate_f')}
FORMULA = 'B=Q(log(div(pe,pe_ttm))); QH=Q(turnover_rate_f); X=B-0.5*QH; F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('earnings_roll_hazard_lowerbound_20d', {})
class Factor_earnings_roll_hazard_lowerbound_20d(BaseFactor):
    name = 'earnings_roll_hazard_lowerbound_20d'
    description = '同日静态与滚动市盈率共享市值分子，两者之比可近似反映滚动盈利相对上一年度盈利的改善，研究业绩更新后的缓慢定价。同时考虑估值或报表信号受到过热交易关注挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。这是盈利变化代理，不把市盈率自身上涨解释为盈利增长。本行条件维度为换手关注拥挤。'
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
            QH = cross_section_rank(values['turnover_rate_f'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
