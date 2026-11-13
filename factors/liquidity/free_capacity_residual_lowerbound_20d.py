"""自由流通日换手容量·共同暴露剥离·保守持续强度。

公式：B=Q(log1p(100*free_share*turnover_rate_f)); Z=Q(cci_bfq); X=Res(B,Z); F=Q(M20(X)-SD20(X))
类别：流动性。业务字段：cci_bfq, free_share, turnover_rate_f。
自由流通股数与换手率共同刻画可吸收交易的实际股数容量，区分高换手小盘股与具备较大承接容量的股票。再剥离价格相对统计通道位置，研究该关系是否只是既有技术或成本状态的伴生现象。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为商品通道位置。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'cci_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cci_bfq'), 'free_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'free_share'), 'turnover_rate_f': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate_f')}
FORMULA = 'B=Q(log1p(100*free_share*turnover_rate_f)); Z=Q(cci_bfq); X=Res(B,Z); F=Q(M20(X)-SD20(X))'

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
@fixed_factor('free_capacity_residual_lowerbound_20d', {})
class Factor_free_capacity_residual_lowerbound_20d(BaseFactor):
    name = 'free_capacity_residual_lowerbound_20d'
    description = '自由流通股数与换手率共同刻画可吸收交易的实际股数容量，区分高换手小盘股与具备较大承接容量的股票。再剥离价格相对统计通道位置，研究该关系是否只是既有技术或成本状态的伴生现象。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为商品通道位置。'
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
            B = cross_section_rank(np.log1p((100 * values['free_share'] * values['turnover_rate_f']).where(100 * values['free_share'] * values['turnover_rate_f'] > -1)).where(eligible))
            Z = cross_section_rank(values['cci_bfq'].where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
