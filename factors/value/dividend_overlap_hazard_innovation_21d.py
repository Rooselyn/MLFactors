"""年度滚动股息交集·供给风险扣减·状态新增信息。

公式：B=Q(sqrt(dv_ratio*dv_ttm)/100); QH=Q(turnover_rate_f); X=B-0.5*QH; F=Q(X-L1(M20(X)))
类别：价值。业务字段：dv_ratio, dv_ttm, turnover_rate_f。
年度与滚动口径均存在较高股息时才给出较高信号，研究分红估值是否具备跨口径连续性，减少单一时点高股息的干扰。同时考虑估值或报表信号受到过热交易关注挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为换手关注拥挤。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'dv_ratio': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ratio'), 'dv_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ttm'), 'turnover_rate_f': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate_f')}
FORMULA = 'B=Q(sqrt(dv_ratio*dv_ttm)/100); QH=Q(turnover_rate_f); X=B-0.5*QH; F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

@register_factor
@fixed_factor('dividend_overlap_hazard_innovation_21d', {})
class Factor_dividend_overlap_hazard_innovation_21d(BaseFactor):
    name = 'dividend_overlap_hazard_innovation_21d'
    description = '年度与滚动口径均存在较高股息时才给出较高信号，研究分红估值是否具备跨口径连续性，减少单一时点高股息的干扰。同时考虑估值或报表信号受到过热交易关注挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为换手关注拥挤。'
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
            B = cross_section_rank((np.sqrt((values['dv_ratio'] * values['dv_ttm']).where(values['dv_ratio'] * values['dv_ttm'] >= 0)) / 100).where(eligible))
            QH = cross_section_rank(values['turnover_rate_f'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
