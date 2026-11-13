"""滚动派现相对年度改善·承接确认·近期相对前期扩散。

公式：B=Q(div(dv_ttm-dv_ratio,abs(dv_ttm)+abs(dv_ratio))); R=(1+sign(B)*Q(T60(net_md_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=Q(M5(X)-L5(M15(X)))
类别：成长。业务字段：dv_ratio, dv_ttm, net_md_amount_ths, net_sm_amount_ths。
比较滚动与年度股息率的相对增量，研究现金分配改善是否比单纯高股息更有持续性。再以同花顺中小单承接判断同向确认：中等订单需求超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。成长指现金分配变化，不能据此认定主营收入增长。本行条件维度为同花顺中小单承接。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'dv_ratio': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ratio'), 'dv_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ttm'), 'net_md_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_amount_ths'), 'net_sm_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_amount_ths')}
FORMULA = 'B=Q(div(dv_ttm-dv_ratio,abs(dv_ttm)+abs(dv_ratio))); R=(1+sign(B)*Q(T60(net_md_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('dividend_roll_confirm_diffusion_20d', {})
class Factor_dividend_roll_confirm_diffusion_20d(BaseFactor):
    name = 'dividend_roll_confirm_diffusion_20d'
    description = '比较滚动与年度股息率的相对增量，研究现金分配改善是否比单纯高股息更有持续性。再以同花顺中小单承接判断同向确认：中等订单需求超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。成长指现金分配变化，不能据此认定主营收入增长。本行条件维度为同花顺中小单承接。'
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
            B = cross_section_rank(divide(values['dv_ttm'] - values['dv_ratio'], abs(values['dv_ttm']) + abs(values['dv_ratio'])).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((time_rank(values['net_md_amount_ths']) - time_rank(values['net_sm_amount_ths'])).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
