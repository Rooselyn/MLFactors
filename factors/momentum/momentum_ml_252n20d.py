"""momentum_ml_252n20d：动量；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from copy import deepcopy
from dataclasses import dataclass
import random
import numpy as np
import pandas as pd
import torch
from torch import nn
from factors.inputs import boolean_values
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
    'amount': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "amount"),
    'turnover_rate': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "turnover_rate"),
    'circ_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "circ_mv"),
    'total_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "total_mv"),
    'pb': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "pb"),
    'ps_ttm': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "ps_ttm"),
    'close': ParquetInput("MLFactors/data/zz500/zz500_daily_index/*/*.parquet", "close", date_column="trade_date", symbol_column=None, filters=(("ts_code", "000905.SH"),)),
    'total_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_assets", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_liab': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_liab", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_hldr_eqy_exc_min_int': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_hldr_eqy_exc_min_int", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_cur_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_cur_assets", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'fix_assets_total': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "fix_assets_total", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'inventories': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "inventories", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "revenue", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'n_income': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "n_income", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'roe': ParquetInput("MLFactors/data/zz500/financial_indicator/*/*.parquet", "roe", date_column="ann_date", announcement_columns=("ann_date",)),
    'roa': ParquetInput("MLFactors/data/zz500/financial_indicator/*/*.parquet", "roa", date_column="ann_date", announcement_columns=("ann_date",)),
    'gross_margin_calc': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "revenue", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='(revenue - oper_cost) / revenue'),
    'operating_expense': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "sell_exp", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='sum_available(sell_exp, admin_exp, fin_exp)'),
    'selling_general_admin': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "sell_exp", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='sum_available(sell_exp, admin_exp)'),
    'netdebt': ParquetInput("MLFactors/data/zz500/financial_indicator/*/*.parquet", "netdebt", date_column="ann_date", announcement_columns=("ann_date",)),
    'fin_exp': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "fin_exp", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'current_ratio': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_cur_assets", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='total_cur_assets / total_cur_liab'),
    'debt_to_equity': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_liab", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='total_liab / total_hldr_eqy_exc_min_int'),
    'available_ann_date': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "f_ann_date", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='coalesce(f_ann_date, ann_date)'),
}



BASE_FEATURE_COUNT = 38

MISSING_INDICATOR_FEATURES = {
    "current_ratio", "current_assets_to_assets", "fixed_assets_to_assets",
    "netdebt_to_assets", "fin_exp_to_revenue", "gross_margin",
    "inventory_to_assets",
}

INPUT_FEATURE_COUNT = BASE_FEATURE_COUNT + len(MISSING_INDICATOR_FEATURES)

@dataclass
class FeatureBundle:
    dates: pd.DatetimeIndex
    symbols: pd.Index
    sample_index: pd.MultiIndex
    date_pos: np.ndarray
    symbol_pos: np.ndarray
    x: np.ndarray
    target_rank: np.ndarray
    formation_returns: np.ndarray
    valid_path: np.ndarray
    feature_names: list[str]
    groups: dict[int, np.ndarray]

def _numeric_panel(
    data: pd.DataFrame,
    column: str,
    dates: pd.DatetimeIndex,
    symbols: pd.Index,
) -> pd.DataFrame:
    values = pd.to_numeric(data[column], errors="coerce")
    return values.unstack("symbol").reindex(index=dates, columns=symbols).astype("float32")

def _date_panel(
    data: pd.DataFrame,
    column: str,
    dates: pd.DatetimeIndex,
    symbols: pd.Index,
) -> pd.DataFrame:
    text = data[column].astype("string").str.replace(r"\.0$", "", regex=True)
    values = pd.to_datetime(text, errors="coerce")
    return values.unstack("symbol").reindex(index=dates, columns=symbols)

def _safe_ratio(numerator: pd.DataFrame, denominator: pd.DataFrame) -> pd.DataFrame:
    return numerator / denominator.where(denominator.abs() > 1e-12)

def build_feature_bundle(
    history: pd.DataFrame,
    eligible_index: pd.MultiIndex,
    min_valid_returns: int,
    benchmark_column: str = "close",
) -> FeatureBundle:
    """构造45维输入（不使用上市日期）、五日前向收益秩和231日形成期收益。"""
    history = history.sort_index()
    dates = pd.DatetimeIndex(history.index.get_level_values("date").unique()).sort_values()
    symbols = pd.Index(history.index.get_level_values("symbol").unique()).sort_values()
    sample_index = eligible_index.unique().sort_values()
    date_pos = dates.get_indexer(sample_index.get_level_values("date"))
    symbol_pos = symbols.get_indexer(sample_index.get_level_values("symbol"))
    keep = (date_pos >= 0) & (symbol_pos >= 0)
    sample_index = sample_index[keep]
    date_pos = date_pos[keep].astype("int32")
    symbol_pos = symbol_pos[keep].astype("int32")

    eligible = np.zeros((len(dates), len(symbols)), dtype=bool)
    eligible[date_pos, symbol_pos] = True
    x = np.empty((len(sample_index), INPUT_FEATURE_COUNT), dtype="float32")
    names: list[str] = []
    missing_columns: list[np.ndarray] = []

    def add(name: str, values: pd.DataFrame) -> None:
        nonlocal x
        values = values.replace([np.inf, -np.inf], np.nan)
        raw = values.to_numpy(copy=False)[date_pos, symbol_pos]
        ranked = values.where(eligible).rank(axis=1, pct=True, method="average")
        selected = ranked.to_numpy(copy=False)[date_pos, symbol_pos]
        x[:, len(names)] = np.nan_to_num(selected * 2.0 - 1.0, nan=0.0).astype("float32")
        names.append(name)
        if name in MISSING_INDICATOR_FEATURES:
            missing_columns.append((~np.isfinite(raw)).astype("float32"))

    price = _numeric_panel(history, 'close_hfq', dates, symbols).ffill()
    log_price = np.log(price.where(price > 0))
    returns = log_price.diff()
    total_mv = _numeric_panel(history, 'total_mv', dates, symbols)
    circ_mv = _numeric_panel(history, "circ_mv", dates, symbols)
    turnover = _numeric_panel(history, "turnover_rate", dates, symbols)
    amount = _numeric_panel(history, "amount", dates, symbols)

    add("log_total_mv", np.log(total_mv.where(total_mv > 0)))
    add("log_circ_mv", np.log(circ_mv.where(circ_mv > 0)))
    add("free_float_ratio", _safe_ratio(circ_mv, total_mv))
    add("turnover_mean_21", turnover.rolling(21, min_periods=15).mean())
    add("turnover_mean_63", turnover.rolling(63, min_periods=45).mean())
    add("turnover_std_63", turnover.rolling(63, min_periods=45).std())
    add("log_amount_mean_21", np.log1p(amount.clip(lower=0)).rolling(21, min_periods=15).mean())
    add("amihud_21", (returns.abs() / amount.where(amount > 0)).rolling(21, min_periods=15).mean())
    add("volatility_21", returns.rolling(21, min_periods=15).std())
    add("volatility_63", returns.rolling(63, min_periods=45).std())
    add("downside_volatility_63", returns.clip(upper=0).pow(2).rolling(63, min_periods=45).mean().pow(0.5))
    add("skewness_63", returns.rolling(63, min_periods=45).skew())
    add("max_return_21", returns.rolling(21, min_periods=15).max())
    add("reversal_21", -price.pct_change(21, fill_method=None))
    add("momentum_63_skip21", price.shift(21) / price.shift(63) - 1.0)
    add("momentum_126_skip21", price.shift(21) / price.shift(126) - 1.0)
    add("momentum_252_skip21", price.shift(21) / price.shift(252) - 1.0)
    add("distance_high_252", price / price.rolling(252, min_periods=200).max() - 1.0)

    benchmark = pd.to_numeric(history[benchmark_column], errors="coerce").groupby(level="date").first()
    benchmark_return = np.log(benchmark.reindex(dates).ffill()).diff()
    market_var = benchmark_return.rolling(252, min_periods=200).var()
    beta = returns.rolling(252, min_periods=200).cov(benchmark_return).div(market_var, axis=0)
    residual_var = returns.rolling(252, min_periods=200).var().sub(beta.pow(2).mul(market_var, axis=0))
    add("beta_252", beta)
    add("idiosyncratic_volatility_252", residual_var.clip(lower=0).pow(0.5))

    total_assets = _numeric_panel(history, "total_assets", dates, symbols)
    revenue = _numeric_panel(history, "revenue", dates, symbols)
    add("book_to_market", 1.0 / _numeric_panel(history, 'pb', dates, symbols).where(lambda value: value > 0))
    add("sales_to_price", 1.0 / _numeric_panel(history, "ps_ttm", dates, symbols).where(lambda value: value > 0))
    add("roe", _numeric_panel(history, "roe", dates, symbols))
    add("roa", _numeric_panel(history, "roa", dates, symbols))
    add("net_profit_margin", _safe_ratio(_numeric_panel(history, 'n_income', dates, symbols), revenue))
    add("gross_margin", _numeric_panel(history, "gross_margin_calc", dates, symbols))
    add("asset_turnover", _safe_ratio(revenue, total_assets))
    add("liabilities_to_assets", _safe_ratio(_numeric_panel(history, 'total_liab', dates, symbols), total_assets))
    add("debt_to_equity", _numeric_panel(history, "debt_to_equity", dates, symbols))
    add("current_ratio", _numeric_panel(history, "current_ratio", dates, symbols))
    add("current_assets_to_assets", _safe_ratio(_numeric_panel(history, 'total_cur_assets', dates, symbols), total_assets))
    add("fixed_assets_to_assets", _safe_ratio(_numeric_panel(history, "fix_assets_total", dates, symbols), total_assets))
    add("netdebt_to_assets", _safe_ratio(_numeric_panel(history, "netdebt", dates, symbols), total_assets))
    add("inventory_to_assets", _safe_ratio(_numeric_panel(history, 'inventories', dates, symbols), total_assets))
    add("opex_to_revenue", _safe_ratio(_numeric_panel(history, "operating_expense", dates, symbols), revenue))
    add("sga_to_revenue", _safe_ratio(_numeric_panel(history, "selling_general_admin", dates, symbols), revenue))
    add("fin_exp_to_revenue", _safe_ratio(_numeric_panel(history, "fin_exp", dates, symbols), revenue))

    date_grid = dates.to_numpy(dtype="datetime64[ns]")[:, None]
    available_ann_date = _date_panel(history, 'available_ann_date', dates, symbols).to_numpy(dtype="datetime64[ns]")
    report_age = (date_grid - available_ann_date) / np.timedelta64(1, "D")
    add("report_age", pd.DataFrame(np.where(report_age >= 0, report_age, np.nan), index=dates, columns=symbols))

    if len(names) != BASE_FEATURE_COUNT:
        raise RuntimeError(f"基础特征数量错误: {len(names)}")
    for offset, values in enumerate(missing_columns, start=BASE_FEATURE_COUNT):
        x[:, offset] = values
    feature_names = names + [f"{name}_missing" for name in names if name in MISSING_INDICATOR_FEATURES]
    if x.shape[1] != INPUT_FEATURE_COUNT or len(feature_names) != INPUT_FEATURE_COUNT:
        raise RuntimeError(f"FFN输入维度必须为{INPUT_FEATURE_COUNT}，实际={x.shape[1]}")

    future = price.shift(-6) / price.shift(-1) - 1.0
    target = future.to_numpy(copy=False)[date_pos, symbol_pos].astype("float32")
    target_rank = (
        pd.Series(target, index=sample_index)
        .groupby(level="date")
        .rank(pct=True, method="average")
        .mul(2.0).sub(1.0).to_numpy(dtype="float32")
    )

    return_array = returns.to_numpy(dtype="float32", copy=True)
    valid = np.isfinite(return_array).astype("int16")
    prefix = np.vstack([np.zeros((1, valid.shape[1]), dtype="int32"), valid.cumsum(axis=0, dtype="int32")])
    path_count = np.zeros(len(sample_index), dtype="int16")
    ready = date_pos >= 252
    path_count[ready] = (
        prefix[date_pos[ready] - 21, symbol_pos[ready]]
        - prefix[date_pos[ready] - 252, symbol_pos[ready]]
    )
    valid_path = path_count >= min_valid_returns

    groups: dict[int, np.ndarray] = {}
    boundaries = np.flatnonzero(np.r_[True, date_pos[1:] != date_pos[:-1], True])
    for left, right in zip(boundaries[:-1], boundaries[1:]):
        groups[int(date_pos[left])] = np.arange(left, right, dtype="int32")

    return FeatureBundle(
        dates=dates, symbols=symbols, sample_index=sample_index,
        date_pos=date_pos, symbol_pos=symbol_pos, x=x,
        target_rank=target_rank, formation_returns=return_array,
        valid_path=valid_path, feature_names=feature_names, groups=groups,
    )

class CMMNetwork(nn.Module):
    """45维输入先升至128维，再逐层降维并输出一个标量。"""

    def __init__(self, hidden_dims: tuple[int, int, int], dropout: float) -> None:
        super().__init__()
        dims = (INPUT_FEATURE_COUNT, *hidden_dims, 1)
        layers: list[nn.Module] = []
        for left, right in zip(dims[:-2], dims[1:-1]):
            layers.extend([nn.Linear(left, right), nn.GELU(), nn.Dropout(dropout)])
        layers.append(nn.Linear(dims[-2], dims[-1]))
        self.network = nn.Sequential(*layers)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features).squeeze(-1)

def rank_ic_loss(
    prediction: torch.Tensor,
    target_rank: torch.Tensor,
    day: torch.Tensor,
) -> torch.Tensor:
    """最大化每日因子值与真实五日前向收益秩的横截面相关。"""
    losses = []
    for value in torch.unique(day):
        selected = day == value
        pred = prediction[selected]
        target = target_rank[selected]
        if pred.numel() < 3:
            continue
        pred = pred - pred.mean()
        target = target - target.mean()
        denominator = pred.square().sum().sqrt() * target.square().sum().sqrt()
        losses.append(1.0 - (pred * target).sum() / denominator.clamp_min(1e-8))
    if not losses:
        return prediction.sum() * 0.0
    return torch.stack(losses).mean()

class AnnualExpandingTrainer:
    def __init__(
        self,
        bundle: FeatureBundle,
        hidden_dims: tuple[int, int, int],
        dropout: float,
        learning_rate: float,
        weight_decay: float,
        max_epochs: int,
        patience: int,
        train_fraction: float,
        batch_dates: int,
        prediction_batch_size: int,
        first_prediction_year: int,
        training_start_year: int,
        seed: int,
        z_cap: float,
        num_threads: int,
    ) -> None:
        self.bundle = bundle
        self.hidden_dims = hidden_dims
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.max_epochs = max_epochs
        self.patience = patience
        self.train_fraction = train_fraction
        self.batch_dates = batch_dates
        self.prediction_batch_size = prediction_batch_size
        self.first_prediction_year = first_prediction_year
        self.training_start_year = training_start_year
        self.seed = seed
        self.z_cap = z_cap
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        torch.set_num_threads(max(1, num_threads))
        self.offsets = np.arange(-252, -21, dtype="int32")

    def _set_seed(self, seed: int) -> None:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

    def _factor_values(
        self,
        model: CMMNetwork,
        indices: np.ndarray,
    ) -> torch.Tensor:
        x = torch.from_numpy(self.bundle.x[indices]).to(self.device)
        date_pos = self.bundle.date_pos[indices]
        symbol_pos = self.bundle.symbol_pos[indices]
        paths = self.bundle.formation_returns[
            date_pos[:, None] + self.offsets[None, :], symbol_pos[:, None]
        ]
        path = torch.from_numpy(paths).to(self.device)
        valid = torch.isfinite(path)
        path = torch.nan_to_num(path)
        raw_z = model(x)
        z = self.z_cap * torch.tanh(raw_z / self.z_cap)
        score = (z[:, None] * path).masked_fill(~valid, -1e9)
        weights = torch.softmax(score, dim=1)
        return (weights * path).sum(dim=1)

    def _groups_for_mask(self, mask: np.ndarray) -> list[np.ndarray]:
        return [
            indices[mask[indices]]
            for indices in self.bundle.groups.values()
            if mask[indices].any()
        ]

    def _predict(
        self,
        model: CMMNetwork,
        groups: list[np.ndarray],
    ) -> tuple[np.ndarray, np.ndarray]:
        indices = np.concatenate(groups) if groups else np.empty(0, dtype="int32")
        output = np.empty(len(indices), dtype="float32")
        model.eval()
        with torch.no_grad():
            for start in range(0, len(indices), self.prediction_batch_size):
                stop = start + self.prediction_batch_size
                output[start:stop] = self._factor_values(
                    model, indices[start:stop]
                ).cpu().numpy()
        return indices, output

    def _exact_rank_ic(
        self,
        model: CMMNetwork,
        groups: list[np.ndarray],
    ) -> float:
        indices, prediction = self._predict(model, groups)
        if not len(indices):
            return float("nan")
        frame = pd.DataFrame({
            "day": self.bundle.date_pos[indices],
            "prediction": prediction,
            "target": self.bundle.target_rank[indices],
        })
        values = frame.groupby("day", sort=False).apply(
            lambda part: part["prediction"].rank().corr(part["target"]),
            include_groups=False,
        )
        return float(values.mean())

    def _fit(
        self,
        train_groups: list[np.ndarray],
        validation_groups: list[np.ndarray],
        year: int,
        warm_state: dict[str, torch.Tensor] | None,
    ) -> tuple[CMMNetwork, dict[str, torch.Tensor]]:
        self._set_seed(self.seed + year)
        model = CMMNetwork(self.hidden_dims, self.dropout).to(self.device)
        if warm_state is not None:
            model.load_state_dict(warm_state)
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
        )
        best_ic = -np.inf
        best_state = deepcopy(model.state_dict())
        stale = 0
        generator = np.random.default_rng(self.seed + year)

        for epoch in range(1, self.max_epochs + 1):
            model.train()
            order = generator.permutation(len(train_groups))
            for start in range(0, len(order), self.batch_dates):
                selected_groups = [
                    train_groups[position]
                    for position in order[start:start + self.batch_dates]
                ]
                indices = np.concatenate(selected_groups)
                prediction = self._factor_values(model, indices)
                target = torch.from_numpy(
                    self.bundle.target_rank[indices]
                ).to(self.device)
                day = torch.from_numpy(self.bundle.date_pos[indices]).to(self.device)
                loss = rank_ic_loss(prediction, target, day)
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            validation_ic = self._exact_rank_ic(model, validation_groups)
            print(
                f"NEW_MOMENTUM year={year} epoch={epoch} "
                f"validation_rank_ic={validation_ic:.6f}",
                flush=True,
            )
            if np.isfinite(validation_ic) and validation_ic > best_ic + 1e-4:
                best_ic = validation_ic
                best_state = deepcopy(model.state_dict())
                stale = 0
            else:
                stale += 1
                if stale >= self.patience:
                    break

        model.load_state_dict(best_state)
        return model, deepcopy(best_state)

    def run(self) -> np.ndarray:
        output = np.full(len(self.bundle.sample_index), np.nan, dtype="float32")
        years = self.bundle.sample_index.get_level_values("date").year.to_numpy()
        finite_target = np.isfinite(self.bundle.target_rank)
        warm_state = None
        final_year = int(years.max())

        for year in range(self.first_prediction_year, final_year + 1):
            test_mask = (years == year) & self.bundle.valid_path
            if not test_mask.any():
                continue
            test_start_pos = int(self.bundle.date_pos[test_mask].min())
            history_mask = (
                (years >= self.training_start_year)
                & (years < year)
                & self.bundle.valid_path
                & finite_target
                & (self.bundle.date_pos + 6 < test_start_pos)
            )
            history_days = np.unique(self.bundle.date_pos[history_mask])
            split = int(len(history_days) * self.train_fraction)
            if split < 1 or split >= len(history_days):
                print(
                    f"NEW_MOMENTUM_SKIP year={year} "
                    f"reason=insufficient_history history_days={len(history_days)}",
                    flush=True,
                )
                continue
            validation_start = int(history_days[split])
            train_mask = history_mask & (
                self.bundle.date_pos < validation_start - 6
            )
            validation_mask = history_mask & (
                self.bundle.date_pos >= validation_start
            )
            train_groups = self._groups_for_mask(train_mask)
            validation_groups = self._groups_for_mask(validation_mask)
            model, warm_state = self._fit(
                train_groups, validation_groups, year, warm_state,
            )
            test_groups = self._groups_for_mask(test_mask)
            indices, prediction = self._predict(model, test_groups)
            output[indices] = prediction
            print(
                f"NEW_MOMENTUM_PREDICT year={year} "
                f"train_days={len(train_groups)} "
                f"validation_days={len(validation_groups)} "
                f"samples={len(indices)}",
                flush=True,
            )
        return output


@register_factor
@fixed_factor('momentum_ml_252n20d', {'history_start': '2010-01-01', 'training_start_year': 2011, 'first_prediction_year': 2014, 'hidden_dims': [128, 64, 16], 'dropout': 0.1, 'learning_rate': 0.001, 'weight_decay': 1e-05, 'max_epochs': 50, 'patience': 5, 'train_fraction': 0.8, 'batch_dates': 16, 'prediction_batch_size': 8192, 'min_valid_returns': 220, 'seed': 42, 'z_cap': 50.0, 'num_threads': 32})
class Factor_momentum_ml_252n20d(BaseFactor):
    INPUTS = INPUTS
    name = 'momentum_ml_252n20d'
    description = "以五日前向Rank IC训练的特征管理动量因子"

    def __init__(
        self,
        history_start: str = "2010-01-01",
        training_start_year: int = 2011,
        first_prediction_year: int = 2014,
        hidden_dims: list[int] | tuple[int, int, int] = (128, 64, 16),
        dropout: float = 0.1,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-5,
        max_epochs: int = 50,
        patience: int = 5,
        train_fraction: float = 0.8,
        batch_dates: int = 16,
        prediction_batch_size: int = 8192,
        min_valid_returns: int = 220,
        seed: int = 42,
        z_cap: float = 50.0,
        num_threads: int = 32,
        universe: str = "zz500",
    ) -> None:
        self.history_start = history_start
        self.training_start_year = training_start_year
        self.first_prediction_year = first_prediction_year
        self.hidden_dims = tuple(hidden_dims)
        if len(self.hidden_dims) != 3 or self.hidden_dims[0] <= INPUT_FEATURE_COUNT:
            raise ValueError(f"hidden_dims必须包含三个隐藏层，且第一层必须高于{INPUT_FEATURE_COUNT}维")
        self.options = dict(
            hidden_dims=self.hidden_dims,
            dropout=dropout,
            learning_rate=learning_rate,
            weight_decay=weight_decay,
            max_epochs=max_epochs,
            patience=patience,
            train_fraction=train_fraction,
            batch_dates=batch_dates,
            prediction_batch_size=prediction_batch_size,
            first_prediction_year=first_prediction_year,
            training_start_year=training_start_year,
            seed=seed,
            z_cap=z_cap,
            num_threads=num_threads,
        )
        self.min_valid_returns = min_valid_returns
        if universe not in {"zz500", "zz1000"}:
            raise ValueError("universe仅支持zz500或zz1000")
        self.universe = universe
        self.history_loader = None
        self.INPUTS = dict(INPUTS)
        benchmark_source = self.INPUTS.pop("close")
        self.INPUTS["close" if universe == "zz500" else f"{universe}_close"] = (
            benchmark_source if universe == "zz500"
            else ParquetInput(None, None, pending=True)
        )

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        if data.empty:
            return pd.DataFrame()
        benchmark_column = "close" if self.universe == "zz500" else f"{self.universe}_close"
        if self.history_loader is None:
            raise ValueError("机器学习训练历史必须由运行层提供 history_loader")
        history = self.history_loader(
            start=self.history_start,
            end=data.index.get_level_values("date").max(),
        )
        training_mask = boolean_values(history["is_member"])
        training_mask &= history.index.get_level_values("date") >= pd.Timestamp(
            f"{self.training_start_year}-01-01"
        )
        training_index = history.index[training_mask]
        status = history.loc[training_index, ["is_st", "is_suspended"]]
        training_index = training_index[
            (~boolean_values(status["is_st"]) & ~boolean_values(status["is_suspended"])).to_numpy()
        ]
        output_start = data.index.get_level_values("date").min()
        early_index = training_index[
            training_index.get_level_values("date") < output_start
        ]
        sample_index = early_index.append(data.index).unique().sort_values()
        bundle = build_feature_bundle(
            history=history,
            eligible_index=sample_index,
            min_valid_returns=self.min_valid_returns,
            benchmark_column=benchmark_column,
        )
        prediction = AnnualExpandingTrainer(bundle=bundle, **self.options).run()
        signals = pd.Series(
            prediction,
            index=bundle.sample_index,
            name=self.name,
        ).unstack("symbol")
        output = signals.reindex(
            index=bundle.dates,
            columns=bundle.symbols,
        ).loc[output_start:]
        eligible = (
            pd.Series(True, index=data.index).unstack("symbol")
            .reindex_like(output).astype("boolean").fillna(False).astype(bool)
        )
        return output.where(eligible)
