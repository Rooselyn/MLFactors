"""开盘竞价成交溢价·原始机制·当日横截面。

公式：B=Q(-log(div(close_opening,vwap_opening))); X=B; F=X
类别：反转。业务字段：close_opening, vwap_opening。
竞价末价格高于该阶段成交均价，反映开盘定价中的临末追价，研究开盘情绪在次日的修正。按当日相对状态研究该机制，较高值表示更偏向所述方向。机制依据：[上交所交易规则](https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml)；[开盘竞价接口](https://tushare.pro/document/2?doc_id=353)和[当日竞价接口](https://tushare.pro/document/2?doc_id=369)用于确认字段定义，日线公式不使用当日信号回填当日交易。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_opening'), 'vwap_opening': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vwap_opening')}
FORMULA = 'B=Q(-log(div(close_opening,vwap_opening))); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('open_auction_premium_raw_level_1d', {})
class Factor_open_auction_premium_raw_level_1d(BaseFactor):
    name = 'open_auction_premium_raw_level_1d'
    description = '竞价末价格高于该阶段成交均价，反映开盘定价中的临末追价，研究开盘情绪在次日的修正。按当日相对状态研究该机制，较高值表示更偏向所述方向。机制依据：[上交所交易规则](https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml)；[开盘竞价接口](https://tushare.pro/document/2?doc_id=353)和[当日竞价接口](https://tushare.pro/document/2?doc_id=369)用于确认字段定义，日线公式不使用当日信号回填当日交易。'
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
            B = cross_section_rank((-np.log(divide(values['close_opening'], values['vwap_opening']).where(divide(values['close_opening'], values['vwap_opening']) > 0))).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
