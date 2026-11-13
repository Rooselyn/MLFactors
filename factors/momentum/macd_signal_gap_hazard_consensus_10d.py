"""趋势差相对信号线·供给风险扣减·方向持续共识。

公式：B=Q(div(macd_dif_bfq-macd_dea_bfq,abs(macd_dif_bfq)+abs(macd_dea_bfq))); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：动量。业务字段：macd_dea_bfq, macd_dif_bfq, rzmre, rzye。
快慢差相对信号线的偏离刻画趋势扩散，而归一化减弱名义价格尺度影响。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为融资买入拥挤。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'macd_dea_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'macd_dea_bfq'), 'macd_dif_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'macd_dif_bfq'), 'rzmre': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzmre'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye')}
FORMULA = 'B=Q(div(macd_dif_bfq-macd_dea_bfq,abs(macd_dif_bfq)+abs(macd_dea_bfq))); QH=Q(div(rzmre,rzye)); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('macd_signal_gap_hazard_consensus_10d', {})
class Factor_macd_signal_gap_hazard_consensus_10d(BaseFactor):
    name = 'macd_signal_gap_hazard_consensus_10d'
    description = '快慢差相对信号线的偏离刻画趋势扩散，而归一化减弱名义价格尺度影响。同时考虑技术强势受到高杠杆新增交易挤压，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为融资买入拥挤。'
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
            B = cross_section_rank(divide(values['macd_dif_bfq'] - values['macd_dea_bfq'], abs(values['macd_dif_bfq']) + abs(values['macd_dea_bfq'])).where(eligible))
            QH = cross_section_rank(divide(values['rzmre'], values['rzye']).where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
