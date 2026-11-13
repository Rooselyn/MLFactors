"""开盘竞价换手热度匹配·原始机制·方向持续共识。

公式：B=Q(div(turnover_rate_auction,1+volume_ratio_auction)); X=B; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：流动性。业务字段：turnover_rate_auction, volume_ratio_auction。
竞价换手相对量比热度越充分，实际可交易筹码参与越多，研究真实承接与单纯关注热度的区别。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'turnover_rate_auction': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate_auction'), 'volume_ratio_auction': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'volume_ratio_auction')}
FORMULA = 'B=Q(div(turnover_rate_auction,1+volume_ratio_auction)); X=B; F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('auction_turnover_efficiency_raw_consensus_10d', {})
class Factor_auction_turnover_efficiency_raw_consensus_10d(BaseFactor):
    name = 'auction_turnover_efficiency_raw_consensus_10d'
    description = '竞价换手相对量比热度越充分，实际可交易筹码参与越多，研究真实承接与单纯关注热度的区别。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。'
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
            B = cross_section_rank(divide(values['turnover_rate_auction'], 1 + values['volume_ratio_auction']).where(eligible))
            X = B
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
