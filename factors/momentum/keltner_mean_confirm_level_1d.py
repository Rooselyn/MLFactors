"""通道中枢均线迁移·承接确认·当日横截面。

公式：B=Q(log(div(ktn_mid_hfq,ma_hfq_30))); R=(1+sign(B)*Q(T60(net_inflow_amount_ths)+T60(main_net_inflow_5d_amount_ths)))/2; X=B*(0.5+R); F=X
类别：动量。业务字段：ktn_mid_hfq, ma_hfq_30, main_net_inflow_5d_amount_ths, net_inflow_amount_ths。
通道中枢相对简单均线抬升，研究不同平滑方式共同揭示的价格重心变化。再以同花顺当日五日需求判断同向确认：当日需求与近期较大订单需求同向活跃时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为同花顺当日五日需求。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'ktn_mid_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ktn_mid_hfq'), 'ma_hfq_30': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ma_hfq_30'), 'main_net_inflow_5d_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'main_net_inflow_5d_amount_ths'), 'net_inflow_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_inflow_amount_ths')}
FORMULA = 'B=Q(log(div(ktn_mid_hfq,ma_hfq_30))); R=(1+sign(B)*Q(T60(net_inflow_amount_ths)+T60(main_net_inflow_5d_amount_ths)))/2; X=B*(0.5+R); F=X'

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
@fixed_factor('keltner_mean_confirm_level_1d', {})
class Factor_keltner_mean_confirm_level_1d(BaseFactor):
    name = 'keltner_mean_confirm_level_1d'
    description = '通道中枢相对简单均线抬升，研究不同平滑方式共同揭示的价格重心变化。再以同花顺当日五日需求判断同向确认：当日需求与近期较大订单需求同向活跃时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为同花顺当日五日需求。'
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
            B = cross_section_rank(np.log(divide(values['ktn_mid_hfq'], values['ma_hfq_30']).where(divide(values['ktn_mid_hfq'], values['ma_hfq_30']) > 0)).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((time_rank(values['net_inflow_amount_ths']) + time_rank(values['main_net_inflow_5d_amount_ths'])).where(eligible))) / 2
            X = B * (0.5 + R)
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
