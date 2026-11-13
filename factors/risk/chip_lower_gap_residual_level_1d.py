"""低成本尾层密度·共同暴露剥离·当日横截面。

公式：B=Q(-div(cost_15pct-cost_5pct,cost_15pct+cost_5pct)); Z=Q(log(div(expma_12_hfq,expma_50_hfq))); X=Res(B,Z); F=X
类别：风险。业务字段：cost_15pct, cost_5pct, expma_12_hfq, expma_50_hfq。
低成本筹码尾层越紧凑，潜在获利盘的退出价格参照越集中，研究下方成本结构的稳定性。再剥离双指数价格趋势，研究该关系是否只是既有技术或成本状态的伴生现象。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为复权双指数趋势。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_15pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_15pct'), 'cost_5pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_5pct'), 'expma_12_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'expma_12_hfq'), 'expma_50_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'expma_50_hfq')}
FORMULA = 'B=Q(-div(cost_15pct-cost_5pct,cost_15pct+cost_5pct)); Z=Q(log(div(expma_12_hfq,expma_50_hfq))); X=Res(B,Z); F=X'

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
@fixed_factor('chip_lower_gap_residual_level_1d', {})
class Factor_chip_lower_gap_residual_level_1d(BaseFactor):
    name = 'chip_lower_gap_residual_level_1d'
    description = '低成本筹码尾层越紧凑，潜在获利盘的退出价格参照越集中，研究下方成本结构的稳定性。再剥离双指数价格趋势，研究该关系是否只是既有技术或成本状态的伴生现象。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为复权双指数趋势。'
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
            B = cross_section_rank((-divide(values['cost_15pct'] - values['cost_5pct'], values['cost_15pct'] + values['cost_5pct'])).where(eligible))
            Z = cross_section_rank(np.log(divide(values['expma_12_hfq'], values['expma_50_hfq']).where(divide(values['expma_12_hfq'], values['expma_50_hfq']) > 0)).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
