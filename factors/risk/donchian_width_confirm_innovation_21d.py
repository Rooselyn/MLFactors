"""唐安奇历史成本宽度·承接确认·状态新增信息。

公式：B=Q(-log(div(taq_up_hfq,taq_down_hfq))); R=(1+sign(B)*Q(net_md_ratio_dc-net_sm_ratio_dc))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))
类别：风险。业务字段：net_md_ratio_dc, net_sm_ratio_dc, taq_down_hfq, taq_up_hfq。
历史上下边界的相对宽度刻画趋势区间内的价格不确定性。再以东方财富中小单差判断同向确认：中等订单承接超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为东方财富中小单差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'net_md_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_ratio_dc'), 'net_sm_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_ratio_dc'), 'taq_down_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'taq_down_hfq'), 'taq_up_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'taq_up_hfq')}
FORMULA = 'B=Q(-log(div(taq_up_hfq,taq_down_hfq))); R=(1+sign(B)*Q(net_md_ratio_dc-net_sm_ratio_dc))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('donchian_width_confirm_innovation_21d', {})
class Factor_donchian_width_confirm_innovation_21d(BaseFactor):
    name = 'donchian_width_confirm_innovation_21d'
    description = '历史上下边界的相对宽度刻画趋势区间内的价格不确定性。再以东方财富中小单差判断同向确认：中等订单承接超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为东方财富中小单差。'
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
            B = cross_section_rank((-np.log(divide(values['taq_up_hfq'], values['taq_down_hfq']).where(divide(values['taq_up_hfq'], values['taq_down_hfq']) > 0))).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((values['net_md_ratio_dc'] - values['net_sm_ratio_dc']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
