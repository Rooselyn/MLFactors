"""随机强弱观测分化·供给风险扣减·当日横截面。

公式：B=Q(T60(rsi_bfq_6)-T60(kdj_bfq)); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=X
类别：反转。业务字段：kdj_bfq, rsi_bfq_6, rzmre, rzye。
相对强弱与随机指标综合输出分化，研究单一震荡指标过热是否缺少另一维度确认。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为融资买入拥挤。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'kdj_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'kdj_bfq'), 'rsi_bfq_6': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rsi_bfq_6'), 'rzmre': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzmre'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye')}
FORMULA = 'B=Q(T60(rsi_bfq_6)-T60(kdj_bfq)); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('kdj_rsi_disagreement_hazard_level_1d', {})
class Factor_kdj_rsi_disagreement_hazard_level_1d(BaseFactor):
    name = 'kdj_rsi_disagreement_hazard_level_1d'
    description = '相对强弱与随机指标综合输出分化，研究单一震荡指标过热是否缺少另一维度确认。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为融资买入拥挤。'
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
            B = cross_section_rank((time_rank(values['rsi_bfq_6']) - time_rank(values['kdj_bfq'])).where(eligible))
            QH = cross_section_rank(divide(values['rzmre'], values['rzye']).where(eligible))
            X = B - 0.5 * QH
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
