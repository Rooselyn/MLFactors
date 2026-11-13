"""自由流通日换手容量·供给风险扣减·方向持续共识。

公式：B=Q(log1p(100*free_share*turnover_rate_f)); QH=Q(ChipTail(chip_price,chip_percent)); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：流动性。业务字段：chip_percent, chip_price, free_share, turnover_rate_f。
自由流通股数与换手率共同刻画可吸收交易的实际股数容量，区分高换手小盘股与具备较大承接容量的股票。同时考虑该机制受到远端筹码供给冲击，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为完整筹码外尾压力。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'free_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'free_share'), 'turnover_rate_f': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate_f'), 'chip_tail': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_tail')}
FORMULA = 'B=Q(log1p(100*free_share*turnover_rate_f)); QH=Q(ChipTail(chip_price,chip_percent)); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('free_capacity_hazard_consensus_10d', {})
class Factor_free_capacity_hazard_consensus_10d(BaseFactor):
    name = 'free_capacity_hazard_consensus_10d'
    description = '自由流通股数与换手率共同刻画可吸收交易的实际股数容量，区分高换手小盘股与具备较大承接容量的股票。同时考虑该机制受到远端筹码供给冲击，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为完整筹码外尾压力。'
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
            B = cross_section_rank(np.log1p((100 * values['free_share'] * values['turnover_rate_f']).where(100 * values['free_share'] * values['turnover_rate_f'] > -1)).where(eligible))
            QH = cross_section_rank(values['chip_tail'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
