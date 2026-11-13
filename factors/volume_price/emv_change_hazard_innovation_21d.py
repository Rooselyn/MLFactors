"""简易波动承接改善·供给风险扣减·状态新增信息。

公式：B=Q(div(emv_hfq-maemv_hfq,abs(emv_hfq)+abs(maemv_hfq))); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=Q(X-L1(M20(X)))
类别：量价。业务字段：emv_hfq, maemv_hfq, rzmre, rzye。
单位交易推动的简易波动指标超过自身平滑项，研究价格推动效率的改善。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为融资买入拥挤。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'emv_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'emv_hfq'), 'maemv_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'maemv_hfq'), 'rzmre': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzmre'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye')}
FORMULA = 'B=Q(div(emv_hfq-maemv_hfq,abs(emv_hfq)+abs(maemv_hfq))); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('emv_change_hazard_innovation_21d', {})
class Factor_emv_change_hazard_innovation_21d(BaseFactor):
    name = 'emv_change_hazard_innovation_21d'
    description = '单位交易推动的简易波动指标超过自身平滑项，研究价格推动效率的改善。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为融资买入拥挤。'
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
            B = cross_section_rank(divide(values['emv_hfq'] - values['maemv_hfq'], abs(values['emv_hfq']) + abs(values['maemv_hfq'])).where(eligible))
            QH = cross_section_rank(divide(values['rzmre'], values['rzye']).where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
