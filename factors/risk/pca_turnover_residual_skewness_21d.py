"""pca_turnover_residual_skewness_21d。

Y_s,i=turnover_rate[s,i],s=t-20..t; Z_s,i=(Y_s,i-Mean_s(Y_i))/Std_s(Y_i,ddof=0); (U,S,V)=SVD(Z); K=2 if S1^2/Sum(S^2)<0.2 else 1; PC=U[:,1:K]*S[1:K]; e_i=OLSResidual(Y_i ~ 1+PC); F=Skew(e_i,bias=False)
先从同一历史窗口的股票换手矩阵提取共同主成分，再度量独立交易强度冲击的不对称性；区别于用规模、价值组合解释换手率的既有显式模型。 原文：[用PCA提取主成分后，再计算残差波动，这个思路能带来显著提升吗？](https://zhuanlan.zhihu.com/p/2074604582391629707)。
完整21日窗口、至少100只共同有效且自身标准差正的股票；不按来源演示代码把缺交易当换手0填充，PCA仅用完整样本。标准化按股票沿时间轴进行，最多2个主成分且阈值依来源20%，含截距OLS以原始换手率为目标；SVD成分正负号不影响残差。特异度按文字取1−R²，源码返回R²只是反向同序口径，二者不另计；含截距且完整样本的残差均值恒近0，不把该中间输出凑成因子。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from scipy import stats
from factors.base import eligibility
INPUTS = {'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate')}
FORMULA = 'Y_s,i=turnover_rate[s,i],s=t-20..t; Z_s,i=(Y_s,i-Mean_s(Y_i))/Std_s(Y_i,ddof=0); (U,S,V)=SVD(Z); K=2 if S1^2/Sum(S^2)<0.2 else 1; PC=U[:,1:K]*S[1:K]; e_i=OLSResidual(Y_i ~ 1+PC); F=Skew(e_i,bias=False)'
RECIPE = {'family': 'pca_turnover', 'variant': 'skewness'}

def finite(x):
    if isinstance(x, (pd.DataFrame, pd.Series)):
        return x.replace([np.inf, -np.inf], np.nan)
    return np.where(np.isfinite(x), x, np.nan) if np.ndim(x) else x if np.isfinite(x) else np.nan

def div(a, b):
    if isinstance(b, (pd.DataFrame, pd.Series)):
        b = b.where(np.isfinite(b) & b.ne(0))
    elif np.ndim(b):
        b = np.where(np.isfinite(b) & (b != 0), b, np.nan)
    elif not np.isfinite(b) or b == 0:
        b = np.nan
    with np.errstate(all='ignore'):
        return finite(a / b)

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    x = v['turnover_rate']
    out = x * np.nan
    for t in range(20, len(x)):
        a = x.iloc[t - 20:t + 1]
        good = a.notna().all() & a.std(ddof=0).gt(0) & e.iloc[t]
        if good.sum() < 100:
            continue
        a = a.loc[:, good].to_numpy()
        z = (a - a.mean(axis=0)) / a.std(axis=0)
        (u, s, _) = np.linalg.svd(z, full_matrices=False)
        k = 2 if s[0] ** 2 / np.sum(s * s) < 0.2 else 1
        design = np.column_stack([np.ones(21), u[:, :k] * s[:k]])
        res = a - design @ np.linalg.lstsq(design, a, rcond=None)[0]
        result = stats.skew(res, axis=0, bias=False)
        out.iloc[t, np.flatnonzero(good)] = result
    return out

def daily_values(data, inputs):
    dates = pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values()
    symbols = data.index.get_level_values('symbol').unique().sort_values()
    values = {}
    for (key, source) in inputs.items():
        if source.announcement_columns or key not in data:
            continue
        field = data[key].unstack('symbol').reindex(index=dates, columns=symbols)
        if source.field.startswith('industry_sw_'):
            field = field.astype('string').replace('', pd.NA)
        else:
            field = finite(field.apply(pd.to_numeric, errors='coerce').astype(float))
            if source.field in ('open', 'high', 'low', 'close', 'open_hfq', 'high_hfq', 'low_hfq', 'close_hfq', 'adj_factor', 'total_mv', 'circ_mv', 'float_share', 'total_share'):
                field = field.where(field > 0)
            elif source.field in ('vol', 'amount'):
                field = field.where(field >= 0)
        values[key] = field
        values[f"{source.path.split('/')[-3]}.{source.field}"] = field
    return (values, dates, symbols)

@register_factor
@fixed_factor('pca_turnover_residual_skewness_21d', {})
class Factor_pca_turnover_residual_skewness_21d(BaseFactor):
    name = 'pca_turnover_residual_skewness_21d'
    description = '先从同一历史窗口的股票换手矩阵提取共同主成分，再度量独立交易强度冲击的不对称性；区别于用规模、价值组合解释换手率的既有显式模型。 原文：[用PCA提取主成分后，再计算残差波动，这个思路能带来显著提升吗？](https://zhuanlan.zhihu.com/p/2074604582391629707)。'
    INPUTS = INPUTS
    FORMULA = FORMULA
    RECIPE = RECIPE
    warmup_days = 100000
    PRESERVE_REPORT_HISTORY = True

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        (v, dates, symbols) = daily_values(data, self.INPUTS)
        if data.empty:
            return pd.DataFrame(index=dates, columns=symbols, dtype=float)
        e = eligibility(data, dates, symbols)
        recipe = self.RECIPE
        with np.errstate(all='ignore'):
            value = compute_daily(recipe, v, e)
        return finite(value).astype(float).where(e).rename_axis(index='date', columns='symbol')
