"""均价相对开盘迁移·共同暴露剥离·保守持续强度。

公式：B=Q(log(div(avg_price,open))); Z=Q(log(div(bbi_hfq,ma_hfq_250))); X=Res(B,Z); F=Q(M20(X)-SD20(X))
类别：动量。业务字段：avg_price, bbi_hfq, ma_hfq_250, open。
全日平均成交价相对开盘上移表示多数成交价格获得抬升，研究全天价格接受度的持续性。再剥离长周期成本位置的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为多空年线距离。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'avg_price': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'avg_price'), 'bbi_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'bbi_hfq'), 'ma_hfq_250': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ma_hfq_250'), 'open': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open')}
FORMULA = 'B=Q(log(div(avg_price,open))); Z=Q(log(div(bbi_hfq,ma_hfq_250))); X=Res(B,Z); F=Q(M20(X)-SD20(X))'

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
@fixed_factor('average_open_move_residual_lowerbound_20d', {})
class Factor_average_open_move_residual_lowerbound_20d(BaseFactor):
    name = 'average_open_move_residual_lowerbound_20d'
    description = '全日平均成交价相对开盘上移表示多数成交价格获得抬升，研究全天价格接受度的持续性。再剥离长周期成本位置的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。本行条件维度为多空年线距离。'
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
            B = cross_section_rank(np.log(divide(values['avg_price'], values['open']).where(divide(values['avg_price'], values['open']) > 0)).where(eligible))
            Z = cross_section_rank(np.log(divide(values['bbi_hfq'], values['ma_hfq_250']).where(divide(values['bbi_hfq'], values['ma_hfq_250']) > 0)).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
