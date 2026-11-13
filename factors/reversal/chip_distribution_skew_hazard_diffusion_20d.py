"""全分布高成本偏斜·供给风险扣减·近期相对前期扩散。

公式：B=Q(-ChipSkew(chip_price,chip_percent)); QH=Q(div(rzye,10000*free_share*open)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))
类别：反转。业务字段：chip_percent, chip_price, free_share, open, rzye。
直接衡量全分布高成本尾部的相对厚度，研究高成本解套供给对反弹持续性的压制。同时考虑成本结构受到杠杆存量挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为融资供给脆弱性。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'free_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'free_share'), 'open': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye'), 'chip_skew': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_skew')}
FORMULA = 'B=Q(-ChipSkew(chip_price,chip_percent)); QH=Q(div(rzye,10000*free_share*open)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('chip_distribution_skew_hazard_diffusion_20d', {})
class Factor_chip_distribution_skew_hazard_diffusion_20d(BaseFactor):
    name = 'chip_distribution_skew_hazard_diffusion_20d'
    description = '直接衡量全分布高成本尾部的相对厚度，研究高成本解套供给对反弹持续性的压制。同时考虑成本结构受到杠杆存量挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为融资供给脆弱性。'
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
            B = cross_section_rank((-values['chip_skew']).where(eligible))
            QH = cross_section_rank(divide(values['rzye'], 10000 * values['free_share'] * values['open']).where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
