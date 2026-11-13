"""开盘至收盘竞价迁移·承接确认·当日横截面。

公式：B=Q(log(div(close_closing,open))); R=(1+sign(B)*Q(main_net_inflow_ratio_dc))/2; X=B*(0.5+R); F=X
类别：动量。业务字段：close_closing, main_net_inflow_ratio_dc, open。
开盘到收盘竞价的同日价格迁移刻画全天需求方向，研究T+1交易约束下需求能否跨日释放。再以东方财富主力净占比判断同向确认：较大订单合计呈现更强净需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为东方财富主力净占比。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_closing'), 'main_net_inflow_ratio_dc': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'main_net_inflow_ratio_dc'), 'open': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open')}
FORMULA = 'B=Q(log(div(close_closing,open))); R=(1+sign(B)*Q(main_net_inflow_ratio_dc))/2; X=B*(0.5+R); F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('intraday_auction_trend_confirm_level_1d', {})
class Factor_intraday_auction_trend_confirm_level_1d(BaseFactor):
    name = 'intraday_auction_trend_confirm_level_1d'
    description = '开盘到收盘竞价的同日价格迁移刻画全天需求方向，研究T+1交易约束下需求能否跨日释放。再以东方财富主力净占比判断同向确认：较大订单合计呈现更强净需求时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为东方财富主力净占比。'
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
            B = cross_section_rank(np.log(divide(values['close_closing'], values['open']).where(divide(values['close_closing'], values['open']) > 0)).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank(values['main_net_inflow_ratio_dc'].where(eligible))) / 2
            X = B * (0.5 + R)
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
