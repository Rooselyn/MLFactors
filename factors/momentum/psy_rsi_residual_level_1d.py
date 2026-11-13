"""心理均衡相对强弱·共同暴露剥离·当日横截面。

公式：B=Q(T60(psyma_hfq)+T60(rsi_hfq_24)); Z=Q(T60(wr1_hfq)-T60(wr_hfq)); X=Res(B,Z); F=X
类别：动量。业务字段：psyma_hfq, rsi_hfq_24, wr1_hfq, wr_hfq。
平滑心理线与较慢相对强弱同时提升，研究不依赖单日尖峰的趋势共识。再剥离超买超卖期限分化，研究该关系是否只是既有技术或成本状态的伴生现象。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为复权威廉期限差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'psyma_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'psyma_hfq'), 'rsi_hfq_24': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rsi_hfq_24'), 'wr1_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'wr1_hfq'), 'wr_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'wr_hfq')}
FORMULA = 'B=Q(T60(psyma_hfq)+T60(rsi_hfq_24)); Z=Q(T60(wr1_hfq)-T60(wr_hfq)); X=Res(B,Z); F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

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
@fixed_factor('psy_rsi_residual_level_1d', {})
class Factor_psy_rsi_residual_level_1d(BaseFactor):
    name = 'psy_rsi_residual_level_1d'
    description = '平滑心理线与较慢相对强弱同时提升，研究不依赖单日尖峰的趋势共识。再剥离超买超卖期限分化，研究该关系是否只是既有技术或成本状态的伴生现象。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为复权威廉期限差。'
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
            B = cross_section_rank((time_rank(values['psyma_hfq']) + time_rank(values['rsi_hfq_24'])).where(eligible))
            Z = cross_section_rank((time_rank(values['wr1_hfq']) - time_rank(values['wr_hfq'])).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
