"""开盘自由流通市值·共同暴露剥离·近期相对前期扩散。

公式：B=Q(-log(10000*free_share*open)); Z=Q(div(brar_ar_hfq-brar_br_hfq,abs(brar_ar_hfq)+abs(brar_br_hfq))); X=Res(B,Z); F=Q(M5(X)-L5(M15(X)))
类别：规模。业务字段：brar_ar_hfq, brar_br_hfq, free_share, open。
以自由流通股本乘开盘价衡量可交易市值，研究A股交易供给较小股票的规模溢价及其容量约束。再剥离人气与买卖意愿偏离，研究该关系是否只是既有技术或成本状态的伴生现象。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。这是开盘口径自由流通市值，不冒充收盘总市值。本行条件维度为复权人气意愿差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'brar_ar_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'brar_ar_hfq'), 'brar_br_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'brar_br_hfq'), 'free_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'free_share'), 'open': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open')}
FORMULA = 'B=Q(-log(10000*free_share*open)); Z=Q(div(brar_ar_hfq-brar_br_hfq,abs(brar_ar_hfq)+abs(brar_br_hfq))); X=Res(B,Z); F=Q(M5(X)-L5(M15(X)))'

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
@fixed_factor('free_cap_residual_diffusion_20d', {})
class Factor_free_cap_residual_diffusion_20d(BaseFactor):
    name = 'free_cap_residual_diffusion_20d'
    description = '以自由流通股本乘开盘价衡量可交易市值，研究A股交易供给较小股票的规模溢价及其容量约束。再剥离人气与买卖意愿偏离，研究该关系是否只是既有技术或成本状态的伴生现象。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。这是开盘口径自由流通市值，不冒充收盘总市值。本行条件维度为复权人气意愿差。'
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
            B = cross_section_rank((-np.log((10000 * values['free_share'] * values['open']).where(10000 * values['free_share'] * values['open'] > 0))).where(eligible))
            Z = cross_section_rank(divide(values['brar_ar_hfq'] - values['brar_br_hfq'], abs(values['brar_ar_hfq']) + abs(values['brar_br_hfq'])).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
