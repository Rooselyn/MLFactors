"""筹码外圈收敛·原始机制·当日横截面。

公式：B=Q(-div(cost_95pct-cost_5pct,cost_95pct+cost_5pct)); X=B; F=X
类别：风险。业务字段：cost_5pct, cost_95pct。
外圈成本跨度越小，潜在持仓盈亏分歧越集中，研究低筹码分歧能否降低急跌时的供给不确定性。按当日相对状态研究该机制，较高值表示更偏向所述方向。字段依据：[筹码分位字段](https://tushare.pro/document/2?doc_id=293)与[筹码价格分布](https://tushare.pro/document/2?doc_id=294)；上述供给效应为本报告提出的研究假说。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_5pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_5pct'), 'cost_95pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_95pct')}
FORMULA = 'B=Q(-div(cost_95pct-cost_5pct,cost_95pct+cost_5pct)); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('chip_outer_raw_level_1d', {})
class Factor_chip_outer_raw_level_1d(BaseFactor):
    name = 'chip_outer_raw_level_1d'
    description = '外圈成本跨度越小，潜在持仓盈亏分歧越集中，研究低筹码分歧能否降低急跌时的供给不确定性。按当日相对状态研究该机制，较高值表示更偏向所述方向。字段依据：[筹码分位字段](https://tushare.pro/document/2?doc_id=293)与[筹码价格分布](https://tushare.pro/document/2?doc_id=294)；上述供给效应为本报告提出的研究假说。'
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
            B = cross_section_rank((-divide(values['cost_95pct'] - values['cost_5pct'], values['cost_95pct'] + values['cost_5pct'])).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
