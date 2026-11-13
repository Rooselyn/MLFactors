"""低振幅分红收益·共同暴露剥离·当日横截面。

公式：B=Q(div(dv_ratio/100,1+abs(swing))); Z=Q(log(div(boll_mid_bfq,ma_bfq_90))); X=Res(B,Z); F=X
类别：价值。业务字段：boll_mid_bfq, dv_ratio, ma_bfq_90, swing。
对高分红同时伴随剧烈日内分歧的股票降低权重，研究分红估值支撑能否在较平稳的交易环境中兑现。再剥离波动中枢相对长期成本的位置，研究该关系是否只是既有技术或成本状态的伴生现象。按当日相对状态研究该机制，较高值表示更偏向所述方向。振幅仅作为同来源相对分歧强度，不赋予未确认的百分比精度。本行条件维度为中轨长期均衡差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'boll_mid_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'boll_mid_bfq'), 'dv_ratio': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ratio'), 'ma_bfq_90': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ma_bfq_90'), 'swing': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'swing')}
FORMULA = 'B=Q(div(dv_ratio/100,1+abs(swing))); Z=Q(log(div(boll_mid_bfq,ma_bfq_90))); X=Res(B,Z); F=X'

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
@fixed_factor('dividend_swing_residual_level_1d', {})
class Factor_dividend_swing_residual_level_1d(BaseFactor):
    name = 'dividend_swing_residual_level_1d'
    description = '对高分红同时伴随剧烈日内分歧的股票降低权重，研究分红估值支撑能否在较平稳的交易环境中兑现。再剥离波动中枢相对长期成本的位置，研究该关系是否只是既有技术或成本状态的伴生现象。按当日相对状态研究该机制，较高值表示更偏向所述方向。振幅仅作为同来源相对分歧强度，不赋予未确认的百分比精度。本行条件维度为中轨长期均衡差。'
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
            B = cross_section_rank(divide(values['dv_ratio'] / 100, 1 + abs(values['swing'])).where(eligible))
            Z = cross_section_rank(np.log(divide(values['boll_mid_bfq'], values['ma_bfq_90']).where(divide(values['boll_mid_bfq'], values['ma_bfq_90']) > 0)).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
