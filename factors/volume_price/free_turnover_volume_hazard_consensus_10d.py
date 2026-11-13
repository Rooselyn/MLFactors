"""换手相对量比承接·供给风险扣减·方向持续共识。

公式：B=Q(div(turnover_rate_f,1+volume_ratio)); QH=Q(ChipCV(chip_price,chip_percent)); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：量价。业务字段：chip_percent, chip_price, turnover_rate_f, volume_ratio。
自由流通换手相对量比越充分，交易需求越可能落实为筹码交换，研究换手承接与关注热度的差异。同时考虑交易强度受到分散成本结构的潜在供给干扰，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为完整筹码相对分歧。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'turnover_rate_f': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate_f'), 'volume_ratio': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'volume_ratio'), 'chip_cv': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_cv')}
FORMULA = 'B=Q(div(turnover_rate_f,1+volume_ratio)); QH=Q(ChipCV(chip_price,chip_percent)); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('free_turnover_volume_hazard_consensus_10d', {})
class Factor_free_turnover_volume_hazard_consensus_10d(BaseFactor):
    name = 'free_turnover_volume_hazard_consensus_10d'
    description = '自由流通换手相对量比越充分，交易需求越可能落实为筹码交换，研究换手承接与关注热度的差异。同时考虑交易强度受到分散成本结构的潜在供给干扰，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为完整筹码相对分歧。'
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
            B = cross_section_rank(divide(values['turnover_rate_f'], 1 + values['volume_ratio']).where(eligible))
            QH = cross_section_rank(values['chip_cv'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
