"""尾盘竞价重定价·原始机制·当日横截面。

公式：B=Q(log(div(vwap_closing,open_closing))); X=B; F=X
类别：动量。业务字段：open_closing, vwap_closing。
收盘竞价成交均价相对该阶段起点上移，刻画尾盘集中需求，研究收盘价格发现的跨日延续。按当日相对状态研究该机制，较高值表示更偏向所述方向。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'open_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_closing'), 'vwap_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vwap_closing')}
FORMULA = 'B=Q(log(div(vwap_closing,open_closing))); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('close_auction_reprice_raw_level_1d', {})
class Factor_close_auction_reprice_raw_level_1d(BaseFactor):
    name = 'close_auction_reprice_raw_level_1d'
    description = '收盘竞价成交均价相对该阶段起点上移，刻画尾盘集中需求，研究收盘价格发现的跨日延续。按当日相对状态研究该机制，较高值表示更偏向所述方向。'
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
            B = cross_section_rank(np.log(divide(values['vwap_closing'], values['open_closing']).where(divide(values['vwap_closing'], values['open_closing']) > 0)).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
