"""竞价成交活跃尾移·共同暴露剥离·方向持续共识。

公式：B=Q(T60(vol_closing)-T60(vol_opening)); Z=Q(div(mass_hfq-ma_mass_hfq,abs(mass_hfq)+abs(ma_mass_hfq))); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：流动性。业务字段：ma_mass_hfq, mass_hfq, vol_closing, vol_opening。
各阶段成交量先相对自身历史排序，再比较活跃程度，研究交易需求是否从早盘情绪转向收盘承接。再剥离复权振幅结构扩张，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为复权梅斯扩张。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'ma_mass_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ma_mass_hfq'), 'mass_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'mass_hfq'), 'vol_closing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol_closing'), 'vol_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol_opening')}
FORMULA = 'B=Q(T60(vol_closing)-T60(vol_opening)); Z=Q(div(mass_hfq-ma_mass_hfq,abs(mass_hfq)+abs(ma_mass_hfq))); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))'

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
@fixed_factor('auction_volume_shift_residual_consensus_10d', {})
class Factor_auction_volume_shift_residual_consensus_10d(BaseFactor):
    name = 'auction_volume_shift_residual_consensus_10d'
    description = '各阶段成交量先相对自身历史排序，再比较活跃程度，研究交易需求是否从早盘情绪转向收盘承接。再剥离复权振幅结构扩张，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为复权梅斯扩张。'
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
            B = cross_section_rank((time_rank(values['vol_closing']) - time_rank(values['vol_opening'])).where(eligible))
            Z = cross_section_rank(divide(values['mass_hfq'] - values['ma_mass_hfq'], abs(values['mass_hfq']) + abs(values['ma_mass_hfq'])).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
