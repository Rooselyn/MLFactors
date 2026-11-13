"""中单主动买卖不平衡·承接确认·方向持续共识。

公式：B=Q(div(buy_md_vol-sell_md_vol,buy_md_vol+sell_md_vol)); R=(1+sign(B)*Q(-ChipCV(chip_price,chip_percent)))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：量价。业务字段：buy_md_vol, chip_percent, chip_price, sell_md_vol。
中单买卖不平衡刻画中等订单的边际需求，研究其与价格发现的关系。再以完整筹码成本集中判断同向确认：较集中的成本结构降低新增资金面对的持仓分歧时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。订单大小仅表示成交分档，不等同于散户或机构的真实身份。本行条件维度为完整筹码成本集中。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'buy_md_vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'buy_md_vol'), 'sell_md_vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'sell_md_vol'), 'chip_cv': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_cv')}
FORMULA = 'B=Q(div(buy_md_vol-sell_md_vol,buy_md_vol+sell_md_vol)); R=(1+sign(B)*Q(-ChipCV(chip_price,chip_percent)))/2; X=B*(0.5+R); F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('order_md_confirm_consensus_10d', {})
class Factor_order_md_confirm_consensus_10d(BaseFactor):
    name = 'order_md_confirm_consensus_10d'
    description = '中单买卖不平衡刻画中等订单的边际需求，研究其与价格发现的关系。再以完整筹码成本集中判断同向确认：较集中的成本结构降低新增资金面对的持仓分歧时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。订单大小仅表示成交分档，不等同于散户或机构的真实身份。本行条件维度为完整筹码成本集中。'
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
            B = cross_section_rank(divide(values['buy_md_vol'] - values['sell_md_vol'], values['buy_md_vol'] + values['sell_md_vol']).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((-values['chip_cv']).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
