"""薛斯慢带相对宽度·共同暴露剥离·方向持续共识。

公式：B=Q(-div(abs(xsii_td3_hfq-xsii_td4_hfq),abs(xsii_td3_hfq)+abs(xsii_td4_hfq))); Z=Q(ChipAsym(chip_price,chip_percent)); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：风险。业务字段：chip_percent, chip_price, xsii_td3_hfq, xsii_td4_hfq。
慢成本带的相对宽度衡量较长周期成本分歧，研究低中期不确定性。再剥离成本均值两侧筹码占比的不对称，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为完整筹码左右质量差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'xsii_td3_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'xsii_td3_hfq'), 'xsii_td4_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'xsii_td4_hfq'), 'chip_asym': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_asym')}
FORMULA = 'B=Q(-div(abs(xsii_td3_hfq-xsii_td4_hfq),abs(xsii_td3_hfq)+abs(xsii_td4_hfq))); Z=Q(ChipAsym(chip_price,chip_percent)); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))'

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
@fixed_factor('xsii_slow_band_residual_consensus_10d', {})
class Factor_xsii_slow_band_residual_consensus_10d(BaseFactor):
    name = 'xsii_slow_band_residual_consensus_10d'
    description = '慢成本带的相对宽度衡量较长周期成本分歧，研究低中期不确定性。再剥离成本均值两侧筹码占比的不对称，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为完整筹码左右质量差。'
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
            B = cross_section_rank((-divide(abs(values['xsii_td3_hfq'] - values['xsii_td4_hfq']), abs(values['xsii_td3_hfq']) + abs(values['xsii_td4_hfq']))).where(eligible))
            Z = cross_section_rank(values['chip_asym'].where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
