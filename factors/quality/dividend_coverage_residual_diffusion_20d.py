"""盈利约束滚动派现能力·共同暴露剥离·近期相对前期扩散。

公式：B=Q(min2(dv_ttm/100,div(1,pe_ttm))); Z=Q(bias1_hfq-bias3_hfq); X=Res(B,Z); F=Q(M5(X)-L5(M15(X)))
类别：质量。业务字段：bias1_hfq, bias3_hfq, dv_ttm, pe_ttm。
用盈利收益率约束股息收益率，偏向同时具备盈利和现金分配能力的公司，降低只因股价下跌而被动形成高股息的影响。再剥离短长期价格乖离的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为复权短长乖离。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'bias1_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'bias1_hfq'), 'bias3_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'bias3_hfq'), 'dv_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'dv_ttm'), 'pe_ttm': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe_ttm')}
FORMULA = 'B=Q(min2(dv_ttm/100,div(1,pe_ttm))); Z=Q(bias1_hfq-bias3_hfq); X=Res(B,Z); F=Q(M5(X)-L5(M15(X)))'

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
@fixed_factor('dividend_coverage_residual_diffusion_20d', {})
class Factor_dividend_coverage_residual_diffusion_20d(BaseFactor):
    name = 'dividend_coverage_residual_diffusion_20d'
    description = '用盈利收益率约束股息收益率，偏向同时具备盈利和现金分配能力的公司，降低只因股价下跌而被动形成高股息的影响。再剥离短长期价格乖离的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为复权短长乖离。'
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
            B = cross_section_rank(np.minimum(values['dv_ttm'] / 100, divide(1, values['pe_ttm'])).where(eligible))
            Z = cross_section_rank((values['bias1_hfq'] - values['bias3_hfq']).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
