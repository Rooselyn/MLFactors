"""竞价成交金额尾移·承接确认·保守持续强度。

公式：B=Q(T60(amount_closing)-T60(amount_opening)); R=(1+sign(B)*Q(net_lg_ratio_ths))/2; X=B*(0.5+R); F=Q(M20(X)-SD20(X))
类别：量价。业务字段：amount_closing, amount_opening, net_lg_ratio_ths。
用各自历史异常度比较竞价金额的首尾分布，研究早盘关注能否沉淀为收盘交易需求。再以同花顺大单占比判断同向确认：较大订单需求在成交结构中占比更高时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为同花顺大单占比。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'amount_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount_closing'), 'amount_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount_opening'), 'net_lg_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_ratio_ths')}
FORMULA = 'B=Q(T60(amount_closing)-T60(amount_opening)); R=(1+sign(B)*Q(net_lg_ratio_ths))/2; X=B*(0.5+R); F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('auction_amount_shift_confirm_lowerbound_20d', {})
class Factor_auction_amount_shift_confirm_lowerbound_20d(BaseFactor):
    name = 'auction_amount_shift_confirm_lowerbound_20d'
    description = '用各自历史异常度比较竞价金额的首尾分布，研究早盘关注能否沉淀为收盘交易需求。再以同花顺大单占比判断同向确认：较大订单需求在成交结构中占比更高时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为同花顺大单占比。'
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
            B = cross_section_rank((time_rank(values['amount_closing']) - time_rank(values['amount_opening'])).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank(values['net_lg_ratio_ths'].where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
