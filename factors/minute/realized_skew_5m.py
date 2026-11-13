"""当日5分钟对数收益的已实现偏度因子。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.base import MinuteFactor
from factors.registry import register_factor
from factors.inputs import ParquetInput, fixed_factor



# 分钟价乘当日复权因子；成交量(股)、成交额(元)不复权。新增月分区自动发现。
MINUTE_INPUTS = {
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", "close", date_column="trade_time", adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "adj_factor")),
}


@register_factor
@fixed_factor('realized_skew_5m', {'min_returns': 30})
class Factor_realized_skew_5m(MinuteFactor):
    """用1分钟收盘价构造5分钟收益，并输出当日日内已实现偏度。"""

    MINUTE_INPUTS = MINUTE_INPUTS
    name = "realized_skew_5m"
    description = "当日5分钟对数收益的已实现偏度"

    def __init__(self, min_returns: int = 30) -> None:
        if (
            isinstance(min_returns, bool)
            or not isinstance(min_returns, (int, np.integer))
            or min_returns < 1
        ):
            raise ValueError("min_returns 必须为正整数")
        super().__init__(minute_fields=("close",), minute_window_days=1)
        self.min_returns = int(min_returns)

    def calculate_daily_factor(
        self,
        trade_date: pd.Timestamp,
        symbols: list[str],
        daily_data: pd.DataFrame,
        minute_data: pd.DataFrame,
    ) -> pd.Series:
        """返回当日每只股票的5分钟已实现偏度。

        仅使用 ``(09:30, 11:30]`` 和 ``(13:00, 15:00]``。每个5分钟桶
        取最后有效收盘价；整桶缺失时不跨桶计算收益。保持原实现的午休衔接
        口径，不计算隔夜收益。
        """
        del daily_data  # 当前因子不使用日频字段，但保留统一分钟因子接口。
        result = pd.Series(np.nan, index=symbols, name=self.name, dtype=float)
        if minute_data.empty or not symbols:
            return result

        data = minute_data[["close"]].reset_index()
        day = pd.Timestamp(trade_date).normalize()
        times = data["trade_time"]
        morning = (times > day + pd.Timedelta(hours=9, minutes=30)) & (
            times <= day + pd.Timedelta(hours=11, minutes=30)
        )
        afternoon = (times > day + pd.Timedelta(hours=13)) & (
            times <= day + pd.Timedelta(hours=15)
        )
        data = data.loc[
            (morning | afternoon)
            & data["symbol"].isin(symbols)
            & np.isfinite(data["close"])
            & data["close"].gt(0)
        ].sort_values(["symbol", "trade_time"], kind="stable")
        data = data.drop_duplicates(["symbol", "trade_time"], keep="last")
        if data.empty:
            return result

        data["bar_time"] = data["trade_time"].dt.ceil("5min")
        closes = data.groupby(["bar_time", "symbol"])["close"].last().unstack("symbol")
        bars = pd.date_range(
            day + pd.Timedelta(hours=9, minutes=35),
            day + pd.Timedelta(hours=11, minutes=30),
            freq="5min",
        ).append(
            pd.date_range(
                day + pd.Timedelta(hours=13, minutes=5),
                day + pd.Timedelta(hours=15),
                freq="5min",
            )
        )
        closes = closes.reindex(index=bars, columns=symbols)
        returns = np.log(closes).diff().replace([np.inf, -np.inf], np.nan)
        count = returns.count()
        sum_squares = returns.pow(2).sum()
        skew = (
            np.sqrt(count)
            * returns.pow(3).sum()
            / sum_squares.where(sum_squares > 0).pow(1.5)
        )
        return (
            skew.where(count >= self.min_returns)
            .rename(self.name)
            .reindex(symbols)
        )
