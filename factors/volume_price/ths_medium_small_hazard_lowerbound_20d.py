"""同花顺中小单占比分化·供给风险扣减·保守持续强度。

公式：B=Q(net_md_ratio_ths-net_sm_ratio_ths); QH=Q(winner_rate); X=B-0.5*QH; F=Q(M20(X)-SD20(X))
类别：量价。业务字段：net_md_ratio_ths, net_sm_ratio_ths, winner_rate。
同来源中单与小单净流入占比之差反映订单层级间的需求迁移，研究订单结构变化而非单一净额。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为获利兑现供给。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'net_md_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_ratio_ths'), 'net_sm_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_ratio_ths'), 'winner_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'winner_rate')}
FORMULA = 'B=Q(net_md_ratio_ths-net_sm_ratio_ths); QH=Q(winner_rate); X=B-0.5*QH; F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

@register_factor
@fixed_factor('ths_medium_small_hazard_lowerbound_20d', {})
class Factor_ths_medium_small_hazard_lowerbound_20d(BaseFactor):
    name = 'ths_medium_small_hazard_lowerbound_20d'
    description = '同来源中单与小单净流入占比之差反映订单层级间的需求迁移，研究订单结构变化而非单一净额。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为获利兑现供给。'
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
            B = cross_section_rank((values['net_md_ratio_ths'] - values['net_sm_ratio_ths']).where(eligible))
            QH = cross_section_rank(values['winner_rate'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
