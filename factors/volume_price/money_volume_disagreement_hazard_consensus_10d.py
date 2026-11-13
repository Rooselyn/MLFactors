"""净额净量历史背离·供给风险扣减·方向持续共识。

公式：B=Q(T60(net_mf_amount)-T60(net_mf_vol)); QH=Q(winner_rate); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))
类别：量价。业务字段：net_mf_amount, net_mf_vol, winner_rate。
净流入金额与数量先各自标准化，识别交易价格及订单构成变化带来的量额背离，研究资金需求的结构升级。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为获利兑现供给。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'net_mf_amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_mf_amount'), 'net_mf_vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_mf_vol'), 'winner_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'winner_rate')}
FORMULA = 'B=Q(T60(net_mf_amount)-T60(net_mf_vol)); QH=Q(winner_rate); X=B-0.5*QH; F=Q(div(M10(X),0.05+M10(abs(X))))'

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
@fixed_factor('money_volume_disagreement_hazard_consensus_10d', {})
class Factor_money_volume_disagreement_hazard_consensus_10d(BaseFactor):
    name = 'money_volume_disagreement_hazard_consensus_10d'
    description = '净流入金额与数量先各自标准化，识别交易价格及订单构成变化带来的量额背离，研究资金需求的结构升级。同时考虑较高获利比例增加资金流入被兑现盘抵消的可能性，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为获利兑现供给。'
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
            B = cross_section_rank((time_rank(values['net_mf_amount']) - time_rank(values['net_mf_vol'])).where(eligible))
            QH = cross_section_rank(values['winner_rate'].where(eligible))
            X = B - 0.5 * QH
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
