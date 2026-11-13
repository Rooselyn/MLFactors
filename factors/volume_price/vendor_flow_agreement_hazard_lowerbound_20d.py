"""跨来源资金需求共振·供给风险扣减·保守持续强度。

公式：B=Q(T60(net_inflow_amount_ths)+T60(main_net_inflow_amount_dc)); QH=Q(winner_rate); X=B-0.5*QH; F=Q(M20(X)-SD20(X))
类别：量价。业务字段：main_net_inflow_amount_dc, net_inflow_amount_ths, winner_rate。
不同来源的资金信号分别标准化后求共振，研究定义不同的需求观测能否提供相互确认。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。不将两来源净额视为同一统计口径，也不直接相加原始金额。本行条件维度为获利兑现供给。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'main_net_inflow_amount_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'main_net_inflow_amount_dc'), 'net_inflow_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_inflow_amount_ths'), 'winner_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'winner_rate')}
FORMULA = 'B=Q(T60(net_inflow_amount_ths)+T60(main_net_inflow_amount_dc)); QH=Q(winner_rate); X=B-0.5*QH; F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('vendor_flow_agreement_hazard_lowerbound_20d', {})
class Factor_vendor_flow_agreement_hazard_lowerbound_20d(BaseFactor):
    name = 'vendor_flow_agreement_hazard_lowerbound_20d'
    description = '不同来源的资金信号分别标准化后求共振，研究定义不同的需求观测能否提供相互确认。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。不将两来源净额视为同一统计口径，也不直接相加原始金额。本行条件维度为获利兑现供给。'
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
            QH = cross_section_rank(values['winner_rate'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
