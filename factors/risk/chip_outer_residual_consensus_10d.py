"""筹码外圈收敛·共同暴露剥离·方向持续共识。

公式：B=Q(-div(cost_95pct-cost_5pct,cost_95pct+cost_5pct)); Z=Q(div(dfma_dif_bfq-dfma_difma_bfq,abs(dfma_dif_bfq)+abs(dfma_difma_bfq))); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：风险。业务字段：cost_5pct, cost_95pct, dfma_dif_bfq, dfma_difma_bfq。
外圈成本跨度越小，潜在持仓盈亏分歧越集中，研究低筹码分歧能否降低急跌时的供给不确定性。再剥离均线差扩张的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为未复权平行线扩张。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_5pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_5pct'), 'cost_95pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_95pct'), 'dfma_dif_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dfma_dif_bfq'), 'dfma_difma_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dfma_difma_bfq')}
FORMULA = 'B=Q(-div(cost_95pct-cost_5pct,cost_95pct+cost_5pct)); Z=Q(div(dfma_dif_bfq-dfma_difma_bfq,abs(dfma_dif_bfq)+abs(dfma_difma_bfq))); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))'

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

@register_factor
@fixed_factor('chip_outer_residual_consensus_10d', {})
class Factor_chip_outer_residual_consensus_10d(BaseFactor):
    name = 'chip_outer_residual_consensus_10d'
    description = '外圈成本跨度越小，潜在持仓盈亏分歧越集中，研究低筹码分歧能否降低急跌时的供给不确定性。再剥离均线差扩张的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为未复权平行线扩张。'
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
            B = cross_section_rank((-divide(values['cost_95pct'] - values['cost_5pct'], values['cost_95pct'] + values['cost_5pct'])).where(eligible))
            Z = cross_section_rank(divide(values['dfma_dif_bfq'] - values['dfma_difma_bfq'], abs(values['dfma_dif_bfq']) + abs(values['dfma_difma_bfq'])).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
