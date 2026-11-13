"""低成本锚附近回稳·原始机制·当日横截面。

公式：B=Q(-abs(log(div(open,cost_15pct)))); X=B; F=X
类别：反转。业务字段：cost_15pct, open。
开盘价贴近低成本筹码锚时，历史低成本持仓提供一个可能的承接参照，研究成本锚附近的均值回归。按当日相对状态研究该机制，较高值表示更偏向所述方向。只度量靠近程度，不把成本锚当作保证有效的支撑线。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_15pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_15pct'), 'open': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open')}
FORMULA = 'B=Q(-abs(log(div(open,cost_15pct)))); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('chip_lower_anchor_raw_level_1d', {})
class Factor_chip_lower_anchor_raw_level_1d(BaseFactor):
    name = 'chip_lower_anchor_raw_level_1d'
    description = '开盘价贴近低成本筹码锚时，历史低成本持仓提供一个可能的承接参照，研究成本锚附近的均值回归。按当日相对状态研究该机制，较高值表示更偏向所述方向。只度量靠近程度，不把成本锚当作保证有效的支撑线。'
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
            B = cross_section_rank((-abs(np.log(divide(values['open'], values['cost_15pct']).where(divide(values['open'], values['cost_15pct']) > 0)))).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
