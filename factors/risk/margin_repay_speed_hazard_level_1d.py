"""融资偿还冲击·供给风险扣减·当日横截面。

公式：B=Q(-div(rzche,rzye)); QH=Q(ChipSkew(chip_price,chip_percent)); X=B-0.5*QH; F=X
类别：风险。业务字段：chip_percent, chip_price, rzche, rzye。
偿还额相对融资存量越大，去杠杆交易越集中，研究偿还冲击对短期承接的挤压。同时考虑杠杆交易与高成本套牢供给相互强化，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为完整筹码高成本尾。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'rzche': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzche'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye'), 'chip_skew': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_skew')}
FORMULA = 'B=Q(-div(rzche,rzye)); QH=Q(ChipSkew(chip_price,chip_percent)); X=B-0.5*QH; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('margin_repay_speed_hazard_level_1d', {})
class Factor_margin_repay_speed_hazard_level_1d(BaseFactor):
    name = 'margin_repay_speed_hazard_level_1d'
    description = '偿还额相对融资存量越大，去杠杆交易越集中，研究偿还冲击对短期承接的挤压。同时考虑杠杆交易与高成本套牢供给相互强化，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为完整筹码高成本尾。'
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
            QH = cross_section_rank(values['chip_skew'].where(eligible))
            X = B - 0.5 * QH
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
