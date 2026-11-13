"""Stockstats

公式：完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=12，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_psl(self, meta: _Meta): self[meta.name] = self._psl(meta.column, meta.as_int)；_psl(self, col_name: str, window: int): col_diff = self._col_diff(col_name)<br>pos = col_diff > 0<br>return self.mov_sum(pos, window) / window * 100；_col_diff(self, col): ret = self[col].diff()<br>ret = self._df_to_series(ret)<br>ret.iloc[0] = 0.0<br>return ret；mov_sum(cls, series, size): return cls._rolling(series, size).sum()；_df_to_series(column): if isinstance(column, pd.DataFrame):<br>    num_col = column.shape[1]<br>    if num_col != 1:<br>        raise ValueError(f'Expected a single column, got {num_col}')<br>    column = column.iloc[:, 0]<br>return column；_rolling(series: pd.Series, window: int): return series.rolling(window, min_periods=1, center=False)；原目录：psl（窗口=12）；追踪：PF01482；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'stockstats_psl_12d', 'engine': 'stockstats', 'parameters': {'column': 'close_12_psl'}, 'minimum': 1}

@register_factor
@fixed_factor('stockstats_psl_12d', {})
class Factor_stockstats_psl_12d(PublicFactor):
    name = 'stockstats_psl_12d'
    description = "完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=12，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_psl(self, meta: _Meta): self[meta.name] = self._psl(meta.column, meta.as_int)；_psl(self, col_name: str, window: int): col_diff = self._col_diff(col_name)<br>pos = col_diff > 0<br>return self.mov_sum(pos, window) / window * 100；_col_diff(self, col): ret = self[col].diff()<br>ret = self._df_to_series(ret)<br>ret.iloc[0] = 0.0<br>return ret；mov_sum(cls, series, size): return cls._rolling(series, size).sum()；_df_to_series(column): if isinstance(column, pd.DataFrame):<br>    num_col = column.shape[1]<br>    if num_col != 1:<br>        raise ValueError(f'Expected a single column, got {num_col}')<br>    column = column.iloc[:, 0]<br>return column；_rolling(series: pd.Series, window: int): return series.rolling(window, min_periods=1, center=False)；原目录：psl（窗口=12）；追踪：PF01482；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
