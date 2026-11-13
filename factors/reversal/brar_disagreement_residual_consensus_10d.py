"""人气意愿强度背离·共同暴露剥离·方向持续共识。

公式：B=Q(-div(brar_ar_bfq-brar_br_bfq,abs(brar_ar_bfq)+abs(brar_br_bfq))); Z=Q(log(div(ema_bfq_60,ema_bfq_250))); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：反转。业务字段：brar_ar_bfq, brar_br_bfq, ema_bfq_250, ema_bfq_60。
人气相对买卖意愿过强可能是情绪先行，研究情绪与成交意愿背离后的修正。再剥离中长期成本位置，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为中长未复权指数差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'brar_ar_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'brar_ar_bfq'), 'brar_br_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'brar_br_bfq'), 'ema_bfq_250': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ema_bfq_250'), 'ema_bfq_60': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ema_bfq_60')}
FORMULA = 'B=Q(-div(brar_ar_bfq-brar_br_bfq,abs(brar_ar_bfq)+abs(brar_br_bfq))); Z=Q(log(div(ema_bfq_60,ema_bfq_250))); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))'

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
@fixed_factor('brar_disagreement_residual_consensus_10d', {})
class Factor_brar_disagreement_residual_consensus_10d(BaseFactor):
    name = 'brar_disagreement_residual_consensus_10d'
    description = '人气相对买卖意愿过强可能是情绪先行，研究情绪与成交意愿背离后的修正。再剥离中长期成本位置，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为中长未复权指数差。'
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
            B = cross_section_rank((-divide(values['brar_ar_bfq'] - values['brar_br_bfq'], abs(values['brar_ar_bfq']) + abs(values['brar_br_bfq']))).where(eligible))
            Z = cross_section_rank(np.log(divide(values['ema_bfq_60'], values['ema_bfq_250']).where(divide(values['ema_bfq_60'], values['ema_bfq_250']) > 0)).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
