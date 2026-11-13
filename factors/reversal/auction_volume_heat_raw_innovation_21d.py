"""开盘竞价放量过热·原始机制·状态新增信息。

公式：B=Q(-T60(vol_auction)*T60(volume_ratio_auction)); X=B; F=Q(X-L1(M20(X)))
类别：反转。业务字段：vol_auction, volume_ratio_auction。
竞价成交量与量比同时处于自身高位时，开盘关注可能被集中透支，研究追价需求耗竭。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'vol_auction': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol_auction'), 'volume_ratio_auction': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'volume_ratio_auction')}
FORMULA = 'B=Q(-T60(vol_auction)*T60(volume_ratio_auction)); X=B; F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('auction_volume_heat_raw_innovation_21d', {})
class Factor_auction_volume_heat_raw_innovation_21d(BaseFactor):
    name = 'auction_volume_heat_raw_innovation_21d'
    description = '竞价成交量与量比同时处于自身高位时，开盘关注可能被集中透支，研究追价需求耗竭。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。'
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
            B = cross_section_rank((-time_rank(values['vol_auction']) * time_rank(values['volume_ratio_auction'])).where(eligible))
            X = B
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
