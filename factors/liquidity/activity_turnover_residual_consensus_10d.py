"""活跃度笔换手匹配·共同暴露剥离·方向持续共识。

公式：B=Q(T60(activity)+T60(avg_turnover)); Z=Q(div(asi_hfq-asit_hfq,abs(asi_hfq)+abs(asit_hfq))); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))
类别：流动性。业务字段：activity, asi_hfq, asit_hfq, avg_turnover。
将交易活跃度与笔换手强度共同标准化，研究交易参与广度和实际换手是否同步扩张。再剥离振动趋势扩张的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为复权振动趋势。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'activity': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'activity'), 'asi_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'asi_hfq'), 'asit_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'asit_hfq'), 'avg_turnover': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'avg_turnover')}
FORMULA = 'B=Q(T60(activity)+T60(avg_turnover)); Z=Q(div(asi_hfq-asit_hfq,abs(asi_hfq)+abs(asit_hfq))); X=Res(B,Z); F=Q(div(M10(X),0.05+M10(abs(X))))'

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
@fixed_factor('activity_turnover_residual_consensus_10d', {})
class Factor_activity_turnover_residual_consensus_10d(BaseFactor):
    name = 'activity_turnover_residual_consensus_10d'
    description = '将交易活跃度与笔换手强度共同标准化，研究交易参与广度和实际换手是否同步扩张。再剥离振动趋势扩张的共同暴露，研究该关系是否只是既有技术或成本状态的伴生现象。比较近10日净方向与绝对强度，偏向反复得到同方向验证的机制，抑制正负交替的噪声。本行条件维度为复权振动趋势。'
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
            B = cross_section_rank((time_rank(values['activity']) + time_rank(values['avg_turnover'])).where(eligible))
            Z = cross_section_rank(divide(values['asi_hfq'] - values['asit_hfq'], abs(values['asi_hfq']) + abs(values['asit_hfq'])).where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = cross_section_rank(divide(X.rolling(10, min_periods=1).mean(), 0.05 + abs(X).rolling(10, min_periods=1).mean()).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
