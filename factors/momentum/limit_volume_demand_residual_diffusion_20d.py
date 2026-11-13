"""涨跌停状态放量需求·共同暴露剥离·近期相对前期扩散。

公式：B=Q(E(limit_status)*log1p(volume_ratio_bak)); Z=Q(bias2_bfq); X=Res(B,Z); F=Q(M5(X)-L5(M15(X)))
类别：动量。业务字段：bias2_bfq, limit_status, volume_ratio_bak。
用实际涨跌状态与量比共同刻画需求方向，研究受价格约束的交易需求是否延迟到后续交易日释放。再剥离中期追价程度的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为中期价格乖离。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'bias2_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'bias2_bfq'), 'limit_status': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'limit_status'), 'volume_ratio_bak': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'volume_ratio_bak')}
FORMULA = 'B=Q(E(limit_status)*log1p(volume_ratio_bak)); Z=Q(bias2_bfq); X=Res(B,Z); F=Q(M5(X)-L5(M15(X)))'

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

def state_direction(value):
    out = pd.DataFrame(0.0, index=value.index, columns=value.columns)
    out = out.mask(value.isin([1, 2, 3]), 1).mask(value.isin([4, 5, 6]), -1)
    return out.where(value.isin([0, 1, 2, 3, 4, 5, 6]))

@register_factor
@fixed_factor('limit_volume_demand_residual_diffusion_20d', {})
class Factor_limit_volume_demand_residual_diffusion_20d(BaseFactor):
    name = 'limit_volume_demand_residual_diffusion_20d'
    description = '用实际涨跌状态与量比共同刻画需求方向，研究受价格约束的交易需求是否延迟到后续交易日释放。再剥离中期追价程度的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为中期价格乖离。'
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
            B = cross_section_rank((state_direction(values['limit_status']) * np.log1p(values['volume_ratio_bak'].where(values['volume_ratio_bak'] > -1))).where(eligible))
            Z = cross_section_rank(values['bias2_bfq'].where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
