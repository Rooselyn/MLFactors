"""价格动量信号加速·共同暴露剥离·状态新增信息。

公式：B=Q(div(mtm_hfq-mtmma_hfq,abs(mtm_hfq)+abs(mtmma_hfq))); Z=Q(trix_bfq-trma_bfq); X=Res(B,Z); F=Q(X-L1(M20(X)))
类别：动量。业务字段：mtm_hfq, mtmma_hfq, trix_bfq, trma_bfq。
价格动量超过其平滑值时，研究趋势新信息相对既有预期的延续。再剥离三重平滑速度变化，研究该关系是否只是既有技术或成本状态的伴生现象。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为未复权三重平滑领先。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'mtm_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'mtm_hfq'), 'mtmma_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'mtmma_hfq'), 'trix_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'trix_bfq'), 'trma_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'trma_bfq')}
FORMULA = 'B=Q(div(mtm_hfq-mtmma_hfq,abs(mtm_hfq)+abs(mtmma_hfq))); Z=Q(trix_bfq-trma_bfq); X=Res(B,Z); F=Q(X-L1(M20(X)))'

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
@fixed_factor('mtm_impulse_residual_innovation_21d', {})
class Factor_mtm_impulse_residual_innovation_21d(BaseFactor):
    name = 'mtm_impulse_residual_innovation_21d'
    description = '价格动量超过其平滑值时，研究趋势新信息相对既有预期的延续。再剥离三重平滑速度变化，研究该关系是否只是既有技术或成本状态的伴生现象。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为未复权三重平滑领先。'
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
            B = cross_section_rank(divide(values['mtm_hfq'] - values['mtmma_hfq'], abs(values['mtm_hfq']) + abs(values['mtmma_hfq'])).where(eligible))
            Z = cross_section_rank((values['trix_bfq'] - values['trma_bfq']).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
