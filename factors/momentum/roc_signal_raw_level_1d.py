"""变化率领先平滑项·原始机制·当日横截面。

公式：B=Q(roc_bfq-maroc_bfq); X=B; F=X
类别：动量。业务字段：maroc_bfq, roc_bfq。
价格变化率超过其平滑预期，研究速度变化而非单纯价格高低。按当日相对状态研究该机制，较高值表示更偏向所述方向。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'maroc_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'maroc_bfq'), 'roc_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'roc_bfq')}
FORMULA = 'B=Q(roc_bfq-maroc_bfq); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

@register_factor
@fixed_factor('roc_signal_raw_level_1d', {})
class Factor_roc_signal_raw_level_1d(BaseFactor):
    name = 'roc_signal_raw_level_1d'
    description = '价格变化率超过其平滑预期，研究速度变化而非单纯价格高低。按当日相对状态研究该机制，较高值表示更偏向所述方向。'
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
            B = cross_section_rank((values['roc_bfq'] - values['maroc_bfq']).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
