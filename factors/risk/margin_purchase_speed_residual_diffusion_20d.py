"""融资滚入速度·共同暴露剥离·近期相对前期扩散。

公式：B=Q(-div(rzmre,rzye)); Z=Q(rsi_hfq_6-rsi_hfq_24); X=Res(B,Z); F=Q(M5(X)-L5(M15(X)))
类别：风险。业务字段：rsi_hfq_24, rsi_hfq_6, rzmre, rzye。
融资买入相对存量余额越快，杠杆仓位更新越集中，研究快速滚入阶段的拥挤和回撤暴露。再剥离短长相对强弱分化，研究该关系是否只是既有技术或成本状态的伴生现象。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为复权强弱期限差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'rsi_hfq_24': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rsi_hfq_24'), 'rsi_hfq_6': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rsi_hfq_6'), 'rzmre': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzmre'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye')}
FORMULA = 'B=Q(-div(rzmre,rzye)); Z=Q(rsi_hfq_6-rsi_hfq_24); X=Res(B,Z); F=Q(M5(X)-L5(M15(X)))'

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
@fixed_factor('margin_purchase_speed_residual_diffusion_20d', {})
class Factor_margin_purchase_speed_residual_diffusion_20d(BaseFactor):
    name = 'margin_purchase_speed_residual_diffusion_20d'
    description = '融资买入相对存量余额越快，杠杆仓位更新越集中，研究快速滚入阶段的拥挤和回撤暴露。再剥离短长相对强弱分化，研究该关系是否只是既有技术或成本状态的伴生现象。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为复权强弱期限差。'
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
            B = cross_section_rank((-divide(values['rzmre'], values['rzye'])).where(eligible))
            Z = cross_section_rank((values['rsi_hfq_6'] - values['rsi_hfq_24']).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
