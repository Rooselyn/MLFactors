"""融资存量竞价承接缺口·共同暴露剥离·当日横截面。

公式：B=Q(-T60(rzye)*(1-T60(amount_auction))); Z=Q(vr_hfq); X=Res(B,Z); F=X
类别：风险。业务字段：amount_auction, rzye, vr_hfq。
融资存量处于高位而竞价承接金额未同步扩张时，杠杆仓位可能缺少边际接盘，研究流动性脆弱性。再剥离成交量结构热度，研究该关系是否只是既有技术或成本状态的伴生现象。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为复权成交比率热度。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'amount_auction': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount_auction'), 'rzye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzye'), 'vr_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vr_hfq')}
FORMULA = 'B=Q(-T60(rzye)*(1-T60(amount_auction))); Z=Q(vr_hfq); X=Res(B,Z); F=X'

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

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('margin_auction_fragility_residual_level_1d', {})
class Factor_margin_auction_fragility_residual_level_1d(BaseFactor):
    name = 'margin_auction_fragility_residual_level_1d'
    description = '融资存量处于高位而竞价承接金额未同步扩张时，杠杆仓位可能缺少边际接盘，研究流动性脆弱性。再剥离成交量结构热度，研究该关系是否只是既有技术或成本状态的伴生现象。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为复权成交比率热度。'
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
            B = cross_section_rank((-time_rank(values['rzye']) * (1 - time_rank(values['amount_auction']))).where(eligible))
            Z = cross_section_rank(values['vr_hfq'].where(eligible))
            X = residual(B.where(eligible), Z.where(eligible))
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
