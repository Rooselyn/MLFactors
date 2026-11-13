"""心理均衡相对强弱·原始机制·近期相对前期扩散。

公式：B=Q(T60(psyma_hfq)+T60(rsi_hfq_24)); X=B; F=Q(M5(X)-L5(M15(X)))
类别：动量。业务字段：psyma_hfq, rsi_hfq_24。
平滑心理线与较慢相对强弱同时提升，研究不依赖单日尖峰的趋势共识。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'psyma_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'psyma_hfq'), 'rsi_hfq_24': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rsi_hfq_24')}
FORMULA = 'B=Q(T60(psyma_hfq)+T60(rsi_hfq_24)); X=B; F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('psy_rsi_raw_diffusion_20d', {})
class Factor_psy_rsi_raw_diffusion_20d(BaseFactor):
    name = 'psy_rsi_raw_diffusion_20d'
    description = '平滑心理线与较慢相对强弱同时提升，研究不依赖单日尖峰的趋势共识。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。'
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
            B = cross_section_rank((time_rank(values['psyma_hfq']) + time_rank(values['rsi_hfq_24'])).where(eligible))
            X = B
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
