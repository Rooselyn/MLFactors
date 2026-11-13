"""内外盘主动需求·承接确认·状态新增信息。

公式：B=Q(div(buying-selling,buying+selling)); R=(1+sign(B)*Q(log(div(close_closing,price_auction))))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))
类别：动量。业务字段：buying, close_closing, price_auction, selling。
外盘相对内盘占优表示主动买入更强，研究主动交易需求在T+1环境下的跨日延续。再以首尾竞价需求接受判断同向确认：交易活跃得到首尾成交价格迁移的确认时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为首尾竞价需求接受。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'buying': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'buying'), 'close_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_closing'), 'price_auction': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'price_auction'), 'selling': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'selling')}
FORMULA = 'B=Q(div(buying-selling,buying+selling)); R=(1+sign(B)*Q(log(div(close_closing,price_auction))))/2; X=B*(0.5+R); F=Q(X-L1(M20(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('active_trade_balance_confirm_innovation_21d', {})
class Factor_active_trade_balance_confirm_innovation_21d(BaseFactor):
    name = 'active_trade_balance_confirm_innovation_21d'
    description = '外盘相对内盘占优表示主动买入更强，研究主动交易需求在T+1环境下的跨日延续。再以首尾竞价需求接受判断同向确认：交易活跃得到首尾成交价格迁移的确认时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为首尾竞价需求接受。'
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
            B = cross_section_rank(divide(values['buying'] - values['selling'], values['buying'] + values['selling']).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank(np.log(divide(values['close_closing'], values['price_auction']).where(divide(values['close_closing'], values['price_auction']) > 0)).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
