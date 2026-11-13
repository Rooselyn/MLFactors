"""布林上下轨分歧·供给风险扣减·保守持续强度。

公式：B=Q(-log(div(boll_upper_bfq,boll_lower_bfq))); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=Q(M20(X)-SD20(X))
类别：风险。业务字段：boll_lower_bfq, boll_upper_bfq, rzmre, rzye。
以同口径上下轨相对宽度刻画近期波动扩张，研究低价格分歧。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为融资买入拥挤。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'boll_lower_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'boll_lower_bfq'), 'boll_upper_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'boll_upper_bfq'), 'rzmre': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzmre'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye')}
FORMULA = 'B=Q(-log(div(boll_upper_bfq,boll_lower_bfq))); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('boll_width_hazard_lowerbound_20d', {})
class Factor_boll_width_hazard_lowerbound_20d(BaseFactor):
    name = 'boll_width_hazard_lowerbound_20d'
    description = '以同口径上下轨相对宽度刻画近期波动扩张，研究低价格分歧。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为融资买入拥挤。'
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
            B = cross_section_rank((-np.log(divide(values['boll_upper_bfq'], values['boll_lower_bfq']).where(divide(values['boll_upper_bfq'], values['boll_lower_bfq']) > 0))).where(eligible))
            QH = cross_section_rank(divide(values['rzmre'], values['rzye']).where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
