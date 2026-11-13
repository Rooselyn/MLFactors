"""跨来源资金需求共振·原始机制·当日横截面。

公式：B=Q(T60(net_inflow_amount_ths)+T60(main_net_inflow_amount_dc)); X=B; F=X
类别：量价。业务字段：main_net_inflow_amount_dc, net_inflow_amount_ths。
不同来源的资金信号分别标准化后求共振，研究定义不同的需求观测能否提供相互确认。按当日相对状态研究该机制，较高值表示更偏向所述方向。不将两来源净额视为同一统计口径，也不直接相加原始金额。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'main_net_inflow_amount_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'main_net_inflow_amount_dc'), 'net_inflow_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_inflow_amount_ths')}
FORMULA = 'B=Q(T60(net_inflow_amount_ths)+T60(main_net_inflow_amount_dc)); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('vendor_flow_agreement_raw_level_1d', {})
class Factor_vendor_flow_agreement_raw_level_1d(BaseFactor):
    name = 'vendor_flow_agreement_raw_level_1d'
    description = '不同来源的资金信号分别标准化后求共振，研究定义不同的需求观测能否提供相互确认。按当日相对状态研究该机制，较高值表示更偏向所述方向。不将两来源净额视为同一统计口径，也不直接相加原始金额。'
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
            B = cross_section_rank((time_rank(values['net_inflow_amount_ths']) + time_rank(values['main_net_inflow_amount_dc'])).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
