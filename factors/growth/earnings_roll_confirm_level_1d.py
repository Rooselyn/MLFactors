"""滚动盈利相对年报改善·承接确认·当日横截面。

公式：B=Q(log(div(pe,pe_ttm))); R=(1+sign(B)*Q(T60(net_lg_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=X
类别：成长。业务字段：net_lg_amount_ths, net_sm_amount_ths, pe, pe_ttm。
同日静态与滚动市盈率共享市值分子，两者之比可近似反映滚动盈利相对上一年度盈利的改善，研究业绩更新后的缓慢定价。再以同花顺大小单承接判断同向确认：较大订单相对小单有更强的边际需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。这是盈利变化代理，不把市盈率自身上涨解释为盈利增长。本行条件维度为同花顺大小单承接。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'net_lg_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_amount_ths'), 'net_sm_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_amount_ths'), 'pe': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe'), 'pe_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe_ttm')}
FORMULA = 'B=Q(log(div(pe,pe_ttm))); R=(1+sign(B)*Q(T60(net_lg_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=X'

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
@fixed_factor('earnings_roll_confirm_level_1d', {})
class Factor_earnings_roll_confirm_level_1d(BaseFactor):
    name = 'earnings_roll_confirm_level_1d'
    description = '同日静态与滚动市盈率共享市值分子，两者之比可近似反映滚动盈利相对上一年度盈利的改善，研究业绩更新后的缓慢定价。再以同花顺大小单承接判断同向确认：较大订单相对小单有更强的边际需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。这是盈利变化代理，不把市盈率自身上涨解释为盈利增长。本行条件维度为同花顺大小单承接。'
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
            B = cross_section_rank(np.log(divide(values['pe'], values['pe_ttm']).where(divide(values['pe'], values['pe_ttm']) > 0)).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((time_rank(values['net_lg_amount_ths']) - time_rank(values['net_sm_amount_ths'])).where(eligible))) / 2
            X = B * (0.5 + R)
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
