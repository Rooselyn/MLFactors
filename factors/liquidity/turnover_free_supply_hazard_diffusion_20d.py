"""笔换手自由流通供给·供给风险扣减·近期相对前期扩散。

公式：B=Q(T60(avg_turnover)*(1-T60(free_share))); QH=Q(ChipCV(chip_price,chip_percent)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))
类别：流动性。业务字段：avg_turnover, chip_percent, chip_price, free_share。
在自由流通供给相对不扩张时观察笔换手活跃度，研究有限可交易筹码的实际周转效率。同时考虑交易强度受到分散成本结构的潜在供给干扰，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为完整筹码相对分歧。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'avg_turnover': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'avg_turnover'), 'free_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'free_share'), 'chip_cv': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_cv')}
FORMULA = 'B=Q(T60(avg_turnover)*(1-T60(free_share))); QH=Q(ChipCV(chip_price,chip_percent)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('turnover_free_supply_hazard_diffusion_20d', {})
class Factor_turnover_free_supply_hazard_diffusion_20d(BaseFactor):
    name = 'turnover_free_supply_hazard_diffusion_20d'
    description = '在自由流通供给相对不扩张时观察笔换手活跃度，研究有限可交易筹码的实际周转效率。同时考虑交易强度受到分散成本结构的潜在供给干扰，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为完整筹码相对分歧。'
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
            B = cross_section_rank((time_rank(values['avg_turnover']) * (1 - time_rank(values['free_share']))).where(eligible))
            QH = cross_section_rank(values['chip_cv'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
