"""人气意愿强度背离·供给风险扣减·近期相对前期扩散。

公式：B=Q(-div(brar_ar_bfq-brar_br_bfq,abs(brar_ar_bfq)+abs(brar_br_bfq))); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))
类别：反转。业务字段：brar_ar_bfq, brar_br_bfq, rzmre, rzye。
人气相对买卖意愿过强可能是情绪先行，研究情绪与成交意愿背离后的修正。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为融资买入拥挤。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'brar_ar_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'brar_ar_bfq'), 'brar_br_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'brar_br_bfq'), 'rzmre': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzmre'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye')}
FORMULA = 'B=Q(-div(brar_ar_bfq-brar_br_bfq,abs(brar_ar_bfq)+abs(brar_br_bfq))); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('brar_disagreement_hazard_diffusion_20d', {})
class Factor_brar_disagreement_hazard_diffusion_20d(BaseFactor):
    name = 'brar_disagreement_hazard_diffusion_20d'
    description = '人气相对买卖意愿过强可能是情绪先行，研究情绪与成交意愿背离后的修正。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为融资买入拥挤。'
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
            B = cross_section_rank((-divide(values['brar_ar_bfq'] - values['brar_br_bfq'], abs(values['brar_ar_bfq']) + abs(values['brar_br_bfq']))).where(eligible))
            QH = cross_section_rank(divide(values['rzmre'], values['rzye']).where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
