"""趋向强度前后变化·承接确认·状态新增信息。

公式：B=Q(div(dmi_adx_hfq-dmi_adxr_hfq,dmi_adx_hfq+dmi_adxr_hfq)); R=(1+sign(B)*Q(net_lg_ratio_ths-net_md_ratio_ths))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))
类别：动量。业务字段：dmi_adx_hfq, dmi_adxr_hfq, net_lg_ratio_ths, net_md_ratio_ths。
当前趋势强度领先回顾强度时，研究有方向趋势由弱转强的阶段。再以同花顺大中单占比判断同向确认：需求占比向更大订单迁移时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为同花顺大中单占比。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'dmi_adx_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dmi_adx_hfq'), 'dmi_adxr_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dmi_adxr_hfq'), 'net_lg_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_ratio_ths'), 'net_md_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_ratio_ths')}
FORMULA = 'B=Q(div(dmi_adx_hfq-dmi_adxr_hfq,dmi_adx_hfq+dmi_adxr_hfq)); R=(1+sign(B)*Q(net_lg_ratio_ths-net_md_ratio_ths))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('dmi_acceleration_confirm_innovation_21d', {})
class Factor_dmi_acceleration_confirm_innovation_21d(BaseFactor):
    name = 'dmi_acceleration_confirm_innovation_21d'
    description = '当前趋势强度领先回顾强度时，研究有方向趋势由弱转强的阶段。再以同花顺大中单占比判断同向确认：需求占比向更大订单迁移时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为同花顺大中单占比。'
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
            B = cross_section_rank(divide(values['dmi_adx_hfq'] - values['dmi_adxr_hfq'], values['dmi_adx_hfq'] + values['dmi_adxr_hfq']).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((values['net_lg_ratio_ths'] - values['net_md_ratio_ths']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
