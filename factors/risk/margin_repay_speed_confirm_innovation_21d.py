"""融资偿还冲击·承接确认·状态新增信息。

公式：B=Q(-div(rzche,rzye)); R=(1+sign(B)*Q(div(buying-selling,buying+selling)))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))
类别：风险。业务字段：buying, rzche, rzye, selling。
偿还额相对融资存量越大，去杠杆交易越集中，研究偿还冲击对短期承接的挤压。再以内外盘主动承接判断同向确认：主动买入需求为杠杆仓位提供交易承接时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为内外盘主动承接。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'buying': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'buying'), 'rzche': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzche'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye'), 'selling': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'selling')}
FORMULA = 'B=Q(-div(rzche,rzye)); R=(1+sign(B)*Q(div(buying-selling,buying+selling)))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('margin_repay_speed_confirm_innovation_21d', {})
class Factor_margin_repay_speed_confirm_innovation_21d(BaseFactor):
    name = 'margin_repay_speed_confirm_innovation_21d'
    description = '偿还额相对融资存量越大，去杠杆交易越集中，研究偿还冲击对短期承接的挤压。再以内外盘主动承接判断同向确认：主动买入需求为杠杆仓位提供交易承接时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为内外盘主动承接。'
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
            B = cross_section_rank((-divide(values['rzche'], values['rzye'])).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank(divide(values['buying'] - values['selling'], values['buying'] + values['selling']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
