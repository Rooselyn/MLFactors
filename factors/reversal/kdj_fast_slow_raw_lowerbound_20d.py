"""随机指标短线过冲·原始机制·保守持续强度。

公式：B=Q(-(kdj_k_hfq-kdj_d_hfq)/100); X=B; F=Q(M20(X)-SD20(X))
类别：反转。业务字段：kdj_d_hfq, kdj_k_hfq。
快随机指标相对慢随机指标跃升过多，研究短线情绪领先平滑状态后的回归。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'kdj_d_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'kdj_d_hfq'), 'kdj_k_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'kdj_k_hfq')}
FORMULA = 'B=Q(-(kdj_k_hfq-kdj_d_hfq)/100); X=B; F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

@register_factor
@fixed_factor('kdj_fast_slow_raw_lowerbound_20d', {})
class Factor_kdj_fast_slow_raw_lowerbound_20d(BaseFactor):
    name = 'kdj_fast_slow_raw_lowerbound_20d'
    description = '快随机指标相对慢随机指标跃升过多，研究短线情绪领先平滑状态后的回归。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。'
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
            B = cross_section_rank((-(values['kdj_k_hfq'] - values['kdj_d_hfq']) / 100).where(eligible))
            X = B
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
