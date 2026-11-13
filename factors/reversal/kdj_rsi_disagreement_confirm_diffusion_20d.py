"""随机强弱观测分化·承接确认·近期相对前期扩散。

公式：B=Q(T60(rsi_bfq_6)-T60(kdj_bfq)); R=(1+sign(B)*Q(T60(net_md_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=Q(M5(X)-L5(M15(X)))
类别：反转。业务字段：kdj_bfq, net_md_amount_ths, net_sm_amount_ths, rsi_bfq_6。
相对强弱与随机指标综合输出分化，研究单一震荡指标过热是否缺少另一维度确认。再以同花顺中小单承接判断同向确认：中等订单需求超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为同花顺中小单承接。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'kdj_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'kdj_bfq'), 'net_md_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_md_amount_ths'), 'net_sm_amount_ths': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'net_sm_amount_ths'), 'rsi_bfq_6': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rsi_bfq_6')}
FORMULA = 'B=Q(T60(rsi_bfq_6)-T60(kdj_bfq)); R=(1+sign(B)*Q(T60(net_md_amount_ths)-T60(net_sm_amount_ths)))/2; X=B*(0.5+R); F=Q(M5(X)-L5(M15(X)))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def time_rank(value, window=60):
    roll = value.rolling(window, min_periods=1)
    return (roll.rank(method='average') - 0.5) / roll.count()

@register_factor
@fixed_factor('kdj_rsi_disagreement_confirm_diffusion_20d', {})
class Factor_kdj_rsi_disagreement_confirm_diffusion_20d(BaseFactor):
    name = 'kdj_rsi_disagreement_confirm_diffusion_20d'
    description = '相对强弱与随机指标综合输出分化，研究单一震荡指标过热是否缺少另一维度确认。再以同花顺中小单承接判断同向确认：中等订单需求超过小额交易情绪时加强正向信号，反向条件加强负向信号，方向不一致时减弱权重，研究有交易或成本条件支持的同类关系。比较最近5日与此前15日的状态均值，检验需求或基本面代理是否由局部变化向近期阶段扩散。本行条件维度为同花顺中小单承接。'
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
            B = cross_section_rank((time_rank(values['rsi_bfq_6']) - time_rank(values['kdj_bfq'])).where(eligible))
            R = (1 + np.sign(B) * cross_section_rank((time_rank(values['net_md_amount_ths']) - time_rank(values['net_sm_amount_ths'])).where(eligible))) / 2
            X = B * (0.5 + R)
            F = cross_section_rank((X.rolling(5, min_periods=1).mean() - X.rolling(15, min_periods=1).mean().shift(5)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
