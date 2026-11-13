"""竞价首尾价格承接·原始机制·保守持续强度。

公式：B=Q(log(div(close_closing,price_auction))); X=B; F=Q(M20(X)-SD20(X))
类别：动量。业务字段：close_closing, price_auction。
用两个阶段的成交价格观察早盘需求能否获得尾盘承接，避免仅依据开盘热度判定持续性。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_closing'), 'price_auction': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'price_auction')}
FORMULA = 'B=Q(log(div(close_closing,price_auction))); X=B; F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('auction_cross_price_raw_lowerbound_20d', {})
class Factor_auction_cross_price_raw_lowerbound_20d(BaseFactor):
    name = 'auction_cross_price_raw_lowerbound_20d'
    description = '用两个阶段的成交价格观察早盘需求能否获得尾盘承接，避免仅依据开盘热度判定持续性。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。'
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
            B = cross_section_rank(np.log(divide(values['close_closing'], values['price_auction']).where(divide(values['close_closing'], values['price_auction']) > 0)).where(eligible))
            X = B
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
