"""东方财富大中单承接·供给风险扣减·状态新增信息。

公式：B=Q(div(net_lg_amount_dc-net_md_amount_dc,abs(net_lg_amount_dc)+abs(net_md_amount_dc))); QH=Q(winner_rate); X=B-0.5*QH; F=Q(X-L1(M20(X)))
类别：量价。业务字段：net_lg_amount_dc, net_md_amount_dc, winner_rate。
用大单与中单净流向的相对差异观察承接是否向更大订单迁移，降低股票绝对成交规模的影响。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为获利兑现供给。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'net_lg_amount_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_amount_dc'), 'net_md_amount_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_amount_dc'), 'winner_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'winner_rate')}
FORMULA = 'B=Q(div(net_lg_amount_dc-net_md_amount_dc,abs(net_lg_amount_dc)+abs(net_md_amount_dc))); QH=Q(winner_rate); X=B-0.5*QH; F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('dc_large_medium_hazard_innovation_21d', {})
class Factor_dc_large_medium_hazard_innovation_21d(BaseFactor):
    name = 'dc_large_medium_hazard_innovation_21d'
    description = '用大单与中单净流向的相对差异观察承接是否向更大订单迁移，降低股票绝对成交规模的影响。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为获利兑现供给。'
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
            B = cross_section_rank(divide(values['net_lg_amount_dc'] - values['net_md_amount_dc'], abs(values['net_lg_amount_dc']) + abs(values['net_md_amount_dc'])).where(eligible))
            QH = cross_section_rank(values['winner_rate'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
