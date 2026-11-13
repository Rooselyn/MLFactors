"""价格资金强度背离·共同暴露剥离·状态新增信息。

公式：B=Q(T60(mfi_hfq)-T60(cci_hfq)); Z=Q(log(div(ema_hfq_5,ema_hfq_20))); X=Res(B,Z); F=Q(X-L1(M20(X)))
类别：量价。业务字段：cci_hfq, ema_hfq_20, ema_hfq_5, mfi_hfq。
资金流量相对商品通道强度更高时，研究资金承接是否先于价格强势。再剥离近端价格趋势，研究该关系是否只是既有技术或成本状态的伴生现象。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为复权近端指数差。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cci_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cci_hfq'), 'ema_hfq_20': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ema_hfq_20'), 'ema_hfq_5': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ema_hfq_5'), 'mfi_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'mfi_hfq')}
FORMULA = 'B=Q(T60(mfi_hfq)-T60(cci_hfq)); Z=Q(log(div(ema_hfq_5,ema_hfq_20))); X=Res(B,Z); F=Q(X-L1(M20(X)))'

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

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('cci_mfi_residual_innovation_21d', {})
class Factor_cci_mfi_residual_innovation_21d(BaseFactor):
    name = 'cci_mfi_residual_innovation_21d'
    description = '资金流量相对商品通道强度更高时，研究资金承接是否先于价格强势。再剥离近端价格趋势，研究该关系是否只是既有技术或成本状态的伴生现象。关注该机制相对截至昨日的20日常态是否出现新增改善，检验缓慢定价而非长期静态差异。本行条件维度为复权近端指数差。'
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
            B = cross_section_rank((time_rank(values['mfi_hfq']) - time_rank(values['cci_hfq'])).where(eligible))
            Z = cross_section_rank(np.log(divide(values['ema_hfq_5'], values['ema_hfq_20']).where(divide(values['ema_hfq_5'], values['ema_hfq_20']) > 0)).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X - X.rolling(20, min_periods=1).mean().shift(1)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
