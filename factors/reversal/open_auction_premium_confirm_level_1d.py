"""开盘竞价成交溢价·承接确认·当日横截面。

公式：B=Q(-log(div(close_opening,vwap_opening))); R=(1+sign(B)*Q(net_lg_ratio_ths-net_md_ratio_ths))/2; X=B*(0.5+R); F=X
类别：反转。业务字段：close_opening, net_lg_ratio_ths, net_md_ratio_ths, vwap_opening。
竞价末价格高于该阶段成交均价，反映开盘定价中的临末追价，研究开盘情绪在次日的修正。再以同花顺大中单占比判断同向确认：需求占比向更大订单迁移时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为同花顺大中单占比。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_opening'), 'net_lg_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_lg_ratio_ths'), 'net_md_ratio_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_ratio_ths'), 'vwap_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vwap_opening')}
FORMULA = 'B=Q(-log(div(close_opening,vwap_opening))); R=(1+sign(B)*Q(net_lg_ratio_ths-net_md_ratio_ths))/2; X=B*(0.5+R); F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('open_auction_premium_confirm_level_1d', {})
class Factor_open_auction_premium_confirm_level_1d(BaseFactor):
    name = 'open_auction_premium_confirm_level_1d'
    description = '竞价末价格高于该阶段成交均价，反映开盘定价中的临末追价，研究开盘情绪在次日的修正。再以同花顺大中单占比判断同向确认：需求占比向更大订单迁移时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为同花顺大中单占比。'
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
            B = cross_section_rank((-np.log(divide(values['close_opening'], values['vwap_opening']).where(divide(values['close_opening'], values['vwap_opening']) > 0))).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((values['net_lg_ratio_ths'] - values['net_md_ratio_ths']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
