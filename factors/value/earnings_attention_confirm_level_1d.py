"""低关注盈利收益·承接确认·当日横截面。

公式：B=Q(div(div(1,pe_ttm),1+volume_ratio)); R=(1+sign(B)*Q(net_elg_ratio_dc-net_lg_ratio_dc))/2; X=B*(0.5+R); F=X
类别：价值。业务字段：net_elg_ratio_dc, net_lg_ratio_dc, pe_ttm, volume_ratio。
将盈利收益率与当日关注强度结合，寻找盈利价格较便宜且尚未受到量比追逐的股票，研究价值修复而非热门股拥挤。再以东方财富超大大单差判断同向确认：超大额需求较普通大额需求更强时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为东方财富超大大单差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'net_elg_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_elg_ratio_dc'), 'net_lg_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_ratio_dc'), 'pe_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe_ttm'), 'volume_ratio': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'volume_ratio')}
FORMULA = 'B=Q(div(div(1,pe_ttm),1+volume_ratio)); R=(1+sign(B)*Q(net_elg_ratio_dc-net_lg_ratio_dc))/2; X=B*(0.5+R); F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('earnings_attention_confirm_level_1d', {})
class Factor_earnings_attention_confirm_level_1d(BaseFactor):
    name = 'earnings_attention_confirm_level_1d'
    description = '将盈利收益率与当日关注强度结合，寻找盈利价格较便宜且尚未受到量比追逐的股票，研究价值修复而非热门股拥挤。再以东方财富超大大单差判断同向确认：超大额需求较普通大额需求更强时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为东方财富超大大单差。'
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
            B = cross_section_rank(divide(divide(1, values['pe_ttm']), 1 + values['volume_ratio']).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((values['net_elg_ratio_dc'] - values['net_lg_ratio_dc']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
