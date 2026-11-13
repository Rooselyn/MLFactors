"""涨跌停锁定换手惩罚·原始机制·近期相对前期扩散。

公式：B=Q(-Lock(limit_status)*log1p(turnover_rate_f)); X=B; F=Q(M5(X)-L5(M15(X)))
类别：风险。业务字段：limit_status, turnover_rate_f。
极端涨跌状态伴随较强换手，可能意味着拥挤退出或高位筹码交换，研究价格约束下的承接风险。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'limit_status': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'limit_status'), 'turnover_rate_f': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate_f')}
FORMULA = 'B=Q(-Lock(limit_status)*log1p(turnover_rate_f)); X=B; F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def state_lock(value):
    return value.isin([2, 3, 5, 6]).astype(float).where(value.isin([0, 1, 2, 3, 4, 5, 6]))

@register_factor
@fixed_factor('limit_turnover_lock_raw_diffusion_20d', {})
class Factor_limit_turnover_lock_raw_diffusion_20d(BaseFactor):
    name = 'limit_turnover_lock_raw_diffusion_20d'
    description = '极端涨跌状态伴随较强换手，可能意味着拥挤退出或高位筹码交换，研究价格约束下的承接风险。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。'
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
            B = cross_section_rank((-state_lock(values['limit_status']) * np.log1p(values['turnover_rate_f'].where(values['turnover_rate_f'] > -1))).where(eligible))
            X = B
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
