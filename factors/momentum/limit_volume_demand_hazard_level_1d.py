"""涨跌停状态放量需求·供给风险扣减·当日横截面。

公式：B=Q(E(limit_status)*log1p(volume_ratio_bak)); QH=Q(ChipCV(chip_price,chip_percent)); X=B-0.5*QH; F=X
类别：动量。业务字段：chip_percent, chip_price, limit_status, volume_ratio_bak。
用实际涨跌状态与量比共同刻画需求方向，研究受价格约束的交易需求是否延迟到后续交易日释放。同时考虑交易强度受到分散成本结构的潜在供给干扰，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为完整筹码相对分歧。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'limit_status': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'limit_status'), 'volume_ratio_bak': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'volume_ratio_bak'), 'chip_cv': ParquetInput('MLFactors/data/zz500/stock_daily_chip_distribution/*/*.parquet', 'chip_price', aggregation='chip_cv')}
FORMULA = 'B=Q(E(limit_status)*log1p(volume_ratio_bak)); QH=Q(ChipCV(chip_price,chip_percent)); X=B-0.5*QH; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def state_direction(value):
    out = pd.DataFrame(0.0, index=value.index, columns=value.columns)
    out = out.mask(value.isin([1, 2, 3]), 1).mask(value.isin([4, 5, 6]), -1)
    return out.where(value.isin([0, 1, 2, 3, 4, 5, 6]))

@register_factor
@fixed_factor('limit_volume_demand_hazard_level_1d', {})
class Factor_limit_volume_demand_hazard_level_1d(BaseFactor):
    name = 'limit_volume_demand_hazard_level_1d'
    description = '用实际涨跌状态与量比共同刻画需求方向，研究受价格约束的交易需求是否延迟到后续交易日释放。同时考虑交易强度受到分散成本结构的潜在供给干扰，扣除该风险暴露，研究经济逻辑在供给约束下的净强度。按当日相对状态研究该机制，较高值表示更偏向所述方向。本行条件维度为完整筹码相对分歧。'
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
            QH = cross_section_rank(values['chip_cv'].where(eligible))
            X = B - 0.5 * QH
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
