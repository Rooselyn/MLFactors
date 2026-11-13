"""逐日 IC 及显著性检验；组合收益只由 return_engine.py 计算。"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
import statsmodels.api as sm

SUMMARY_METRIC_COLUMNS = ("IC_mean", "IC_std", "ICIR", "t_stat", "p_value")

@dataclass
class FactorEvalResult:
    summary: pd.DataFrame
    full_ic_series: pd.Series




def calc_ic_panel(factor: pd.DataFrame, returns: pd.DataFrame, method: str = "rank") -> pd.Series:
    """一次性按行计算横截面相关，秩在成对有效股票集合内重算。"""
    a = factor.reindex(index=returns.index, columns=returns.columns).astype(float)
    b = returns.astype(float)
    valid = np.isfinite(a) & np.isfinite(b)
    a, b = a.where(valid), b.where(valid)
    if method == "rank":
        a, b = a.rank(axis=1, method="average"), b.rank(axis=1, method="average")
    x = a.sub(a.mean(axis=1), axis=0).to_numpy()
    y = b.sub(b.mean(axis=1), axis=0).to_numpy()
    numerator = np.nansum(x*y, axis=1)
    denominator = np.sqrt(np.nansum(x*x, axis=1)*np.nansum(y*y, axis=1))
    values = np.divide(numerator, denominator, out=np.full(len(a), np.nan), where=denominator>0)
    values[valid.sum(axis=1).to_numpy()<3] = np.nan
    return pd.Series(values, index=returns.index, name="IC").loc[returns.notna().any(axis=1)]


def calc_ic_series(factor, returns, method: str = "rank") -> pd.Series:
    def wide(values):
        if isinstance(values, pd.DataFrame) and not isinstance(values.index, pd.MultiIndex):
            return values
        if isinstance(values, pd.DataFrame): values = values.iloc[:,0]
        return values.unstack(level=1)
    return calc_ic_panel(wide(factor), wide(returns), method)


def calc_offset_ic_stats(ic_series: pd.Series, period: int = 1) -> dict[str, float]:
    """逐日IC的等权均值、样本标准差及均值/标准差，不对offset均值二次平均。"""
    if period <= 0: raise ValueError("period必须为正整数")
    values = pd.to_numeric(ic_series, errors="coerce").replace([np.inf,-np.inf],np.nan).dropna()
    mean = float(values.mean()) if len(values) else np.nan
    std = float(values.std(ddof=1)) if len(values)>1 else np.nan
    return {"IC_mean":mean,"IC_std":std,"ICIR":mean/std if np.isfinite(std) and std>0 else np.nan}


def calc_t_stat(
    ic_series: pd.Series,
    period: int = 1,
    maxlags: int | None = None,
) -> tuple[float, float]:
    """使用 Newey-West / HAC 标准误检验 IC 均值是否显著偏离零。

    Parameters
    ----------
    ic_series : pd.Series
        按时间排列的 IC 序列。

    period : int, default=1
        前瞻收益窗口覆盖的 IC 观测期数。

        例如：
        - 每日计算 IC，使用未来 1 日收益：period=1
        - 每日计算 IC，使用未来 5 日收益：period=5
        - 每日计算 IC，使用未来 20 日收益：period=20

    maxlags : int | None, default=None
        HAC 最大滞后阶数。

        默认使用 period - 1，对收益窗口重合导致的序列相关
        进行修正。

        可以显式指定更大的值，以处理 IC 本身额外存在的
        时间序列相关性。

    Returns
    -------
    tuple[float, float]
        HAC 修正后的 ``(t_stat, p_value)``。
    """
    if period <= 0:
        raise ValueError("period 必须为正整数")

    values = (
        ic_series
        .sort_index()
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .astype(float)
    )

    n_obs = len(values)

    if n_obs < 3:
        return np.nan, np.nan

    # h 期收益最多产生 h - 1 阶机械重叠
    if maxlags is None:
        maxlags = period - 1

    if maxlags < 0:
        raise ValueError("maxlags 不能小于 0")

    # HAC 滞后阶数不能超过样本数量减 1
    maxlags = min(maxlags, n_obs - 1)

    # IC_t = alpha + epsilon_t
    # alpha 即 IC 样本均值
    X = np.ones((n_obs, 1), dtype=float)

    result = sm.OLS(
        endog=values.to_numpy(),
        exog=X,
    ).fit(
        cov_type="HAC",
        cov_kwds={
            "maxlags": maxlags,
            "use_correction": True,
        },
        use_t=True,
    )

    t_stat = result.tvalues[0]
    p_value = result.pvalues[0]

    return float(t_stat), float(p_value)



def calc_forward_returns(
    market_data: pd.DataFrame,
    period: int,
    price_col: str = 'close_hfq',
) -> pd.Series:
    """根据价格面板计算指定周期的未来持有收益。

    计算口径为在因子日后的第一个交易日价格买入，并在再向后 ``period``
    个交易日的价格卖出：``price[t+1+period] / price[t+1] - 1``。这种口径
    避免直接使用因子形成日收盘价成交。结果尾部因缺少未来价格会自然缺失。

    Parameters
    ----------
    market_data : pd.DataFrame
        索引为 ``(date, symbol)`` 的行情数据。
    period : int
        未来持有交易日数量，必须为正整数。
    price_col : str, default "close_hfq"
        用于计算收益的价格列。

    Returns
    -------
    pd.Series
        ``(date, symbol)`` MultiIndex 收益 Series，名称为
        ``fwd_ret_<period>``。

    Raises
    ------
    ValueError
        ``period`` 不是正整数，或缺少指定价格列时抛出。
    """
    if period <= 0:
        raise ValueError("period 必须为正整数")
    if price_col not in market_data.columns:
        raise ValueError(f"market_data 缺少未来收益价格列: {price_col}")
    price = market_data[price_col].unstack()
    return (
        price.shift(-(1 + period)) / price.shift(-1) - 1
    ).stack().rename(f"fwd_ret_{period}")



def eval(factor_values, market_data: pd.DataFrame, forward_period: int = 1,
         ic_method: str = "rank", price_col: str = "close_hfq",
         forward_returns=None) -> FactorEvalResult:
    """只评估预测标签的IC；标签收益不作为可交易组合收益或报告收益。"""
    if forward_period <= 0:
        raise ValueError("forward_period必须为正整数")
    if forward_returns is None:
        forward_returns = calc_forward_returns(market_data, forward_period, price_col)
    ic = calc_ic_series(factor_values, forward_returns, ic_method)
    summary = calc_offset_ic_stats(ic, forward_period)
    t_stat, p_value = calc_t_stat(ic, forward_period)
    summary.update(t_stat=t_stat, p_value=p_value)
    return FactorEvalResult(
        summary=pd.DataFrame([summary], index=pd.Index([forward_period], name="period")),
        full_ic_series=ic,
    )
