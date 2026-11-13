"""净额净量历史背离·共同暴露剥离·方向持续共识。

公式：B=Q(T60(net_mf_amount)-T60(net_mf_vol)); Z=Q(ChipSkew(chip_price,chip_percent)); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：量价。业务字段：chip_percent, chip_price, net_mf_amount, net_mf_vol。
净流入金额与数量先各自标准化，识别交易价格及订单构成变化带来的量额背离，研究资金需求的结构升级。再剥离高成本筹码尾部形状，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为完整筹码高成本偏斜。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'net_mf_amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_mf_amount'), 'net_mf_vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_mf_vol'), 'chip_skew': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_skew')}
FORMULA = 'B=Q(T60(net_mf_amount)-T60(net_mf_vol)); Z=Q(ChipSkew(chip_price,chip_percent)); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

def residual(y, z):
    """逐日横截面含截距OLS；常数解释变量时仅去均值。"""
    valid = np.isfinite(y) & np.isfinite(z)
    (yy, zz) = (y.where(valid), z.where(valid))
    yc = yy.sub(yy.mean(axis=1), axis=0)
    zc = zz.sub(zz.mean(axis=1), axis=0)
    denominator = zc.pow(2).sum(axis=1)
    slope = (yc * zc).sum(axis=1).div(denominator.where(denominator > 0)).fillna(0)
    return yc - zc.mul(slope, axis=0)

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('money_volume_disagreement_residual_consensus_10d', {})
class Factor_money_volume_disagreement_residual_consensus_10d(BaseFactor):
    name = 'money_volume_disagreement_residual_consensus_10d'
    description = '净流入金额与数量先各自标准化，识别交易价格及订单构成变化带来的量额背离，研究资金需求的结构升级。再剥离高成本筹码尾部形状，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为完整筹码高成本偏斜。'
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
            Z = cross_section_rank(values['chip_skew'].where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
