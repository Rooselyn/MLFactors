"""三重平滑速度领先·共同暴露剥离·状态新增信息。

公式：B=Q(trix_hfq-trma_hfq); Z=Q(ChipSkew(chip_price,chip_percent)); X=Res(B,Z); F=Q(X-L1(M20(X)))
类别：动量。业务字段：chip_percent, chip_price, trix_hfq, trma_hfq。
三重平滑变化率超过自身信号线时，研究过滤高频噪声后的趋势加速。再剥离高成本筹码尾部形状，研究该关系是否只是既有技术或成本状态的伴生现象。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为完整筹码高成本偏斜。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'trix_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'trix_hfq'), 'trma_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'trma_hfq'), 'chip_skew': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_skew')}
FORMULA = 'B=Q(trix_hfq-trma_hfq); Z=Q(ChipSkew(chip_price,chip_percent)); X=Res(B,Z); F=Q(X-L1(M20(X)))'

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

@register_factor
@fixed_factor('trix_signal_residual_innovation_21d', {})
class Factor_trix_signal_residual_innovation_21d(BaseFactor):
    name = 'trix_signal_residual_innovation_21d'
    description = '三重平滑变化率超过自身信号线时，研究过滤高频噪声后的趋势加速。再剥离高成本筹码尾部形状，研究该关系是否只是既有技术或成本状态的伴生现象。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为完整筹码高成本偏斜。'
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
            B = cross_section_rank((values['trix_hfq'] - values['trma_hfq']).where(eligible))
            Z = cross_section_rank(values['chip_skew'].where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
