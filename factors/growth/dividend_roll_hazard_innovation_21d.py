"""滚动派现相对年度改善·供给风险扣减·状态新增信息。

公式：B=Q(div(dv_ttm-dv_ratio,abs(dv_ttm)+abs(dv_ratio))); QH=Q(turnover_rate_f); X=B-0.5*QH; F=Q(X-L1(M20(X)))
类别：成长。业务字段：dv_ratio, dv_ttm, turnover_rate_f。
比较滚动与年度股息率的相对增量，研究现金分配改善是否比单纯高股息更有持续性。同时考虑估值或报表信号受到过热交易关注挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。成长指现金分配变化，不能据此认定主营收入增长。本行条件维度为换手关注拥挤。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'dv_ratio': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ratio'), 'dv_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ttm'), 'turnover_rate_f': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate_f')}
FORMULA = 'B=Q(div(dv_ttm-dv_ratio,abs(dv_ttm)+abs(dv_ratio))); QH=Q(turnover_rate_f); X=B-0.5*QH; F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('dividend_roll_hazard_innovation_21d', {})
class Factor_dividend_roll_hazard_innovation_21d(BaseFactor):
    name = 'dividend_roll_hazard_innovation_21d'
    description = '比较滚动与年度股息率的相对增量，研究现金分配改善是否比单纯高股息更有持续性。同时考虑估值或报表信号受到过热交易关注挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。成长指现金分配变化，不能据此认定主营收入增长。本行条件维度为换手关注拥挤。'
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
            B = cross_section_rank(divide(values['dv_ttm'] - values['dv_ratio'], abs(values['dv_ttm']) + abs(values['dv_ratio'])).where(eligible))
            QH = cross_section_rank(values['turnover_rate_f'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
