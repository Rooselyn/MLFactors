"""振幅相对量比冲击·承接确认·近期相对前期扩散。

公式：B=Q(-div(T60(swing),0.5+T60(volume_ratio))); R=(1+sign(B)*Q(log(div(close_closing,price_auction))))/2; X=B*(0.5+R); F=Q(M5(X)-L5(M15(X)))
类别：风险。业务字段：close_closing, price_auction, swing, volume_ratio。
较小成交关注就引起较大日内波动意味着价格冲击偏高，研究交易深度不足带来的风险。再以首尾竞价需求接受判断同向确认：交易活跃得到首尾成交价格迁移的确认时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为首尾竞价需求接受。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_closing'), 'price_auction': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'price_auction'), 'swing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'swing'), 'volume_ratio': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'volume_ratio')}
FORMULA = 'B=Q(-div(T60(swing),0.5+T60(volume_ratio))); R=(1+sign(B)*Q(log(div(close_closing,price_auction))))/2; X=B*(0.5+R); F=Q(M5(X)-L5(M15(X)))'

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
@fixed_factor('swing_volume_impact_confirm_diffusion_20d', {})
class Factor_swing_volume_impact_confirm_diffusion_20d(BaseFactor):
    name = 'swing_volume_impact_confirm_diffusion_20d'
    description = '较小成交关注就引起较大日内波动意味着价格冲击偏高，研究交易深度不足带来的风险。再以首尾竞价需求接受判断同向确认：交易活跃得到首尾成交价格迁移的确认时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为首尾竞价需求接受。'
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
            B = cross_section_rank((-divide(time_rank(values['swing']), 0.5 + time_rank(values['volume_ratio']))).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank(np.log(divide(values['close_closing'], values['price_auction']).where(divide(values['close_closing'], values['price_auction']) > 0)).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
