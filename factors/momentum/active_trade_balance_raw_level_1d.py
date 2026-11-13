"""内外盘主动需求·原始机制·当日横截面。

公式：B=Q(div(buying-selling,buying+selling)); X=B; F=X
类别：动量。业务字段：buying, selling。
外盘相对内盘占优表示主动买入更强，研究主动交易需求在T+1环境下的跨日延续。按当日相对状态研究该机制，较高值表示更偏向所述方向。状态以实际 limit_status 编码为准，不对所有板块统一硬编码10%涨跌幅；收益方向是交易约束下的待检验推断。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'buying': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'buying'), 'selling': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'selling')}
FORMULA = 'B=Q(div(buying-selling,buying+selling)); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('active_trade_balance_raw_level_1d', {})
class Factor_active_trade_balance_raw_level_1d(BaseFactor):
    name = 'active_trade_balance_raw_level_1d'
    description = '外盘相对内盘占优表示主动买入更强，研究主动交易需求在T+1环境下的跨日延续。按当日相对状态研究该机制，较高值表示更偏向所述方向。状态以实际 limit_status 编码为准，不对所有板块统一硬编码10%涨跌幅；收益方向是交易约束下的待检验推断。'
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
            B = cross_section_rank(divide(values['buying'] - values['selling'], values['buying'] + values['selling']).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
