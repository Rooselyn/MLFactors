"""新高新低回溯优势·承接确认·状态新增信息。

公式：B=Q(log1p(topdays)-log1p(lowdays)); R=(1+sign(B)*Q(net_elg_ratio_dc-net_lg_ratio_dc))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))
类别：动量。业务字段：lowdays, net_elg_ratio_dc, net_lg_ratio_dc, topdays。
比较新高与新低对应的回溯跨度，研究突破影响是否覆盖更长历史成本区间。再以东方财富超大大单差判断同向确认：超大额需求较普通大额需求更强时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为东方财富超大大单差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'lowdays': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'lowdays'), 'net_elg_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_elg_ratio_dc'), 'net_lg_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_ratio_dc'), 'topdays': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'topdays')}
FORMULA = 'B=Q(log1p(topdays)-log1p(lowdays)); R=(1+sign(B)*Q(net_elg_ratio_dc-net_lg_ratio_dc))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

@register_factor
@fixed_factor('record_horizon_confirm_innovation_21d', {})
class Factor_record_horizon_confirm_innovation_21d(BaseFactor):
    name = 'record_horizon_confirm_innovation_21d'
    description = '比较新高与新低对应的回溯跨度，研究突破影响是否覆盖更长历史成本区间。再以东方财富超大大单差判断同向确认：超大额需求较普通大额需求更强时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为东方财富超大大单差。'
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
            B = cross_section_rank((np.log1p(values['topdays'].where(values['topdays'] > -1)) - np.log1p(values['lowdays'].where(values['lowdays'] > -1))).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((values['net_elg_ratio_dc'] - values['net_lg_ratio_dc']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
