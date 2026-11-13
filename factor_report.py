"""独立输出MD及交互HTML；HTML增加原始和中性化版本的组合、大盘收益曲线。"""
from __future__ import annotations
import hashlib
import html
import importlib
import json
from pathlib import Path
import re
from typing import Any
import numpy as np
import pandas as pd
from scipy import stats
from dataloader import portable_payload, portable_path, read_factor_output
from factors.base import PublicFactor
from factors.registry import MINUTE_CATEGORY
from factors_eval import calc_forward_returns, calc_ic_panel, calc_offset_ic_stats, calc_t_stat

REPORT_START = pd.Timestamp('2020-01-01')
REPORT_END = pd.Timestamp('2026-06-30')
IC_DECAY_PERIODS = (5,10,15,20,40,60)

CUSTOM_FACTOR_FORMULAS = {
    "cfp_1d": r"\frac{\mathrm{OCF}_t}{\mathrm{MarketCap}_t}",
    "current_liability_ratio_1d": r"\frac{\mathrm{CurrentLiabilities}_t}{\mathrm{TotalLiabilities}_t}",
    "current_ratio_1d": r"\frac{\mathrm{CurrentAssets}_t}{\mathrm{CurrentLiabilities}_t}",
    "debt_per_share_1d": r"\frac{\mathrm{TotalDebt}_t}{\mathrm{BasicShares}_t}",
    "debt_to_asset_1d": r"\frac{\mathrm{TotalLiabilities}_t}{\mathrm{TotalAssets}_t}",
    "dip_rebound_10d": r"\frac{1}{10}\sum_{k=0}^{9}\ln\!\left(\frac{C_{t-k}}{L_{t-k}}\right)",
    "eps_growth_63d": r"\frac{\mathrm{EPS}_t-\mathrm{EPS}_{t-63}}{|\mathrm{EPS}_{t-63}|}",
    "equity_growth_63d": r"\frac{\mathrm{Equity}_t-\mathrm{Equity}_{t-63}}{|\mathrm{Equity}_{t-63}|}",
    "fixed_ratio_1d": r"\frac{\mathrm{NetPPE}_t}{\mathrm{TotalAssets}_t}",
    "gross_margin_1d": r"\frac{\mathrm{GrossProfit}_t}{\mathrm{Revenue}_t}",
    "high_r_std_84d": r"\operatorname{Std}_{84}\!\left(\frac{H_t}{C_{t-1}}-1\right)",
    "hml_r_std_84d": r"\operatorname{Std}_{84}\!\left(\frac{H_t}{C_{t-1}}-1\right)-\operatorname{Std}_{84}\!\left(\frac{L_t}{C_{t-1}}-1\right)",
    "industry_momentum_252n1d": r"\frac{1}{N_{\mathcal I(i),t}-1}\sum_{j\in\mathcal I(i),\,j\ne i}\left(\frac{C_{j,t-1}}{C_{j,t-252}}-1\right)",
    "inventory_turnover_1d": r"\frac{\mathrm{CostOfRevenue}_t}{\mathrm{Inventory}_t}",
    "long_term_debt_ratio_1d": r"\frac{\mathrm{NonCurrentDebt}_t}{\mathrm{TotalAssets}_t}",
    "max_daily_return_top5_21d": r"\frac{1}{5}\sum_{r\in\operatorname{Top5}\{r_{t-20},\ldots,r_t\}}r",
    "net_income_cash_ratio_1d": r"\frac{\mathrm{OCF}_t}{\mathrm{NetIncome}_t}",
    "net_income_growth_63d": r"\frac{\mathrm{NetIncome}_t-\mathrm{NetIncome}_{t-63}}{|\mathrm{NetIncome}_{t-63}|}",
    "net_profit_margin_1d": r"\frac{\mathrm{NetIncome}_t}{\mathrm{Revenue}_t}",
    "momentum_ml_252n20d": r"\sum_{d=22}^{252}\operatorname{Softmax}_d\!\left(\operatorname{FFN}(x_{i,t})r_{i,t-d}\right)r_{i,t-d}",
    "open_high_surge_10d": r"\frac{1}{10}\sum_{k=0}^{9}\ln\!\left(\frac{H_{t-k}}{O_{t-k}}\right)",
    "operating_expense_ratio_1d": r"\frac{\mathrm{OperatingExpense}_t}{\mathrm{Revenue}_t}",
    "quick_ratio_1d": r"\frac{\mathrm{CurrentAssets}_t-\mathrm{Inventory}_t}{\mathrm{CurrentLiabilities}_t}",
    "realized_skew_5m": (
        r"\frac{\sqrt{n}\sum_{k=1}^{n}r_{i,t,k}^{3}}"
        r"{\left(\sum_{k=1}^{n}r_{i,t,k}^{2}\right)^{3/2}},\quad "
        r"r_{i,t,k}=\ln C_{i,t,k}^{5m}-\ln C_{i,t,k-1}^{5m}"
    ),
    "r_std_84d": r"\operatorname{Std}_{84}(r_t),\qquad r_t=\frac{C_t}{C_{t-1}}-1",
    "revenue_growth_63d": r"\frac{\mathrm{Revenue}_t-\mathrm{Revenue}_{t-63}}{|\mathrm{Revenue}_{t-63}|}",
    "reversal_20d": r"-\left(\frac{C_t}{C_{t-20}}-1\right)",
    "reversal_60d": r"-\left(\frac{C_t}{C_{t-60}}-1\right)",
    "roe_growth_63d": r"\frac{\mathrm{ROE}_t-\mathrm{ROE}_{t-63}}{|\mathrm{ROE}_{t-63}|}",
    "size_factor_1d": r"\ln(\mathrm{MarketCap}_t)",
    "size_squared_1d": r"\left[\ln(\mathrm{MarketCap}_t)\right]^2",
    "slp_reversal_20d": r"-\frac{C_t-C_k}{C_k(t-k)},\qquad k=\text{20日窗口内较近的最高或最低价位置}",
    "smallcap_growth_1d": r"Z_{\mathrm{CS}}\!\left[\operatorname{Winsor}_{1\%,99\%}\!\left(-\ln\mathrm{MarketCap}_t\right)\right]",
    "sp_1d": r"\frac{\mathrm{MarketCap}_t}{\mathrm{Revenue}_t}",
    "total_asset_growth_63d": r"\frac{\mathrm{TotalAssets}_t-\mathrm{TotalAssets}_{t-63}}{|\mathrm{TotalAssets}_{t-63}|}",
    "total_asset_turnover_1d": r"\frac{\mathrm{Revenue}_t}{\mathrm{TotalAssets}_t}",
    "trading_amount_20d": r"\frac{1}{20}\sum_{k=0}^{19}C_{t-k}V_{t-k}",
    "turnover_cv_20d": r"\frac{\operatorname{Std}_{20}(\mathrm{Turnover}_t)}{\operatorname{Mean}_{20}(\mathrm{Turnover}_t)},\quad \mathrm{Turnover}_t=\frac{V_tC_t}{\mathrm{MarketCap}_t}",
    "vff3_63d": r"\operatorname{Std}_{63}(\varepsilon_t),\quad r_t=\alpha+\beta_M\mathrm{MKT}_t+\beta_S\mathrm{SMB}_t+\beta_H\mathrm{HML}_t+\varepsilon_t",
    "vff3_up_63d": r"\operatorname{Std}_{63}(\varepsilon_t\mid\varepsilon_t>0)",
    "vff3_upd_63d": r"\operatorname{Std}_{63}(\varepsilon_t\mid\varepsilon_t>0)+\operatorname{Std}_{63}(\varepsilon_t\mid\varepsilon_t<0)",
    "volume_60d": r"\frac{1}{60}\sum_{k=0}^{59}V_{t-k}",
    "volume_price_corr_10d": r"\operatorname{Corr}_{10}\!\left(C_t,\frac{V_tC_t}{\mathrm{MarketCap}_t}\right)",
}

def _public_factor_formula(factor_name: str, config: dict[str, Any]) -> str | None:
    """读取独立实现文件中已有的完整定义，保留本地数值约定及来源。"""
    if config.get('params', {}).get('expansion_kind'):
        return None
    module_name = config.get("module")
    if not module_name:
        return None
    module = importlib.import_module(module_name)
    factor_class = getattr(module, config["relay_class"])
    if not issubclass(factor_class, PublicFactor):
        return None
    if factor_class.SPEC.get("name") != factor_name:
        raise ValueError(f"公开因子 {factor_name} 的实现定义与配置名称不一致")
    _, marker, definition = (module.__doc__ or "").partition("\n公式：")
    definition, footer, _ = definition.partition("\n实现约定见")
    if not marker or not footer or not definition.strip():
        raise ValueError(f"公开因子 {factor_name} 的实现文件缺少完整公式定义")
    return html.unescape(definition.strip()).replace("\n", "<br>")


def factor_formula(factor_name: str, config: dict[str, Any]) -> str:
    """Return the report formula without depending on aggregation code."""
    if config.get("formula"):
        return str(config["formula"])
    params = config.get("params", {})
    expansion_kind = params.get("expansion_kind")
    if expansion_kind == "single_transform":
        base = params["input_factors"][0].replace("_", r"\_")
        return params["formula"] + rf"\qquad u=Z_v\!\left(\mathrm{{{base}}}\right)"
    if expansion_kind == "factor_combination":
        formula = params["formula"].replace("×", r"\times")
        for operator in ('ABS', 'SOFT', 'POS'):
            formula = formula.replace(operator + '(', rf'\operatorname{{{operator}}}(')
        def replace_factor_token(match: re.Match[str]) -> str:
            escaped_name = match.group(2).replace("_", r"\_")
            return (
                rf"\operatorname{{{match.group(1)}}}\!\left("
                rf"\mathrm{{{escaped_name}}}\right)"
            )
        rendered = re.sub(
            r"\b([XZS])\(([A-Za-z0-9_]+)\)",
            replace_factor_token,
            formula,
        )
        if 'SOFT(' in params['formula']:
            rendered += r'\qquad \operatorname{SOFT}(u)=\frac{u}{1+|u|}'
        if 'ABS(' in params['formula']:
            rendered += r'\qquad \operatorname{ABS}(u)=|u|'
        return rendered
    if factor_name in CUSTOM_FACTOR_FORMULAS:
        return CUSTOM_FACTOR_FORMULAS[factor_name]
    operation = str(params.get("operation", "")).upper()
    window = params.get("window", 1)
    exclude_recent = params.get("exclude_recent")
    if exclude_recent is not None:
        price_count = window - exclude_recent + 1
        change_count = window - exclude_recent
        net_formulas = {
            "BETA": rf"\frac{{\operatorname{{Slope}}(C_{{t-{window}:t-{exclude_recent}}}\sim\mathrm{{time}})}}{{C_{{t-{exclude_recent}}}}}",
            "RANK": rf"\operatorname{{PercentileRank}}\!\left(C_{{t-{exclude_recent}}};C_{{t-{window}:t-{exclude_recent}}}\right)",
            "IMAX": rf"\frac{{\operatorname{{argmax}}(H_{{t-{window}:t-{exclude_recent}}})+1}}{{{price_count}}}",
            "IMXD": rf"\frac{{\operatorname{{argmax}}(H_{{t-{window}:t-{exclude_recent}}})-\operatorname{{argmin}}(L_{{t-{window}:t-{exclude_recent}}})}}{{{price_count}}}",
            "RSV": rf"\frac{{C_{{t-{exclude_recent}}}-\min(L_{{t-{window}:t-{exclude_recent}}})}}{{\max(H_{{t-{window}:t-{exclude_recent}}})-\min(L_{{t-{window}:t-{exclude_recent}}})}}",
            "CNTP": rf"\frac{{1}}{{{change_count}}}\sum_{{s=t-{window}+1}}^{{t-{exclude_recent}}}\mathbf 1[C_s>C_{{s-1}}]",
            "CNTD": rf"\frac{{1}}{{{change_count}}}\sum_{{s=t-{window}+1}}^{{t-{exclude_recent}}}\left(\mathbf 1[C_s>C_{{s-1}}]-\mathbf 1[C_s<C_{{s-1}}]\right)",
            "SUMP": rf"\frac{{\sum_{{s=t-{window}+1}}^{{t-{exclude_recent}}}\max(\Delta C_s,0)}}{{\sum_{{s=t-{window}+1}}^{{t-{exclude_recent}}}|\Delta C_s|}}",
            "SUMD": rf"\frac{{\sum_{{s=t-{window}+1}}^{{t-{exclude_recent}}}\max(\Delta C_s,0)-\sum_{{s=t-{window}+1}}^{{t-{exclude_recent}}}\max(-\Delta C_s,0)}}{{\sum_{{s=t-{window}+1}}^{{t-{exclude_recent}}}|\Delta C_s|}}",
        }
        if operation not in net_formulas:
            raise ValueError(f"因子 {factor_name} 缺少剔近期窗口公式")
        return net_formulas[operation]
    formulas = {
        "HIGH0": r"\frac{H_t}{C_t}", "LOW0": r"\frac{L_t}{C_t}",
        "OPEN0": r"\frac{O_t}{C_t}", "VWAP0": r"\frac{\mathrm{VWAP}_t}{C_t}",
        "KMID": r"\frac{C_t-O_t}{O_t}", "KMID2": r"\frac{C_t-O_t}{H_t-L_t}",
        "KUP": r"\frac{H_t-\max(O_t,C_t)}{O_t}", "KUP2": r"\frac{H_t-\max(O_t,C_t)}{H_t-L_t}",
        "KLOW": r"\frac{\min(O_t,C_t)-L_t}{O_t}", "KLOW2": r"\frac{\min(O_t,C_t)-L_t}{H_t-L_t}",
        "KSFT": r"\frac{2C_t-H_t-L_t}{O_t}", "KSFT2": r"\frac{2C_t-H_t-L_t}{H_t-L_t}",
        "KLEN": r"\frac{H_t-L_t}{O_t}",
        "BETA": rf"\frac{{\operatorname{{Slope}}(C_{{t-{window}+1:t}}\sim\mathrm{{time}})}}{{C_t}}",
        "RESI": rf"\frac{{\operatorname{{Residual}}_t(C_{{t-{window}+1:t}}\sim\mathrm{{time}})}}{{C_t}}",
        "RSQR": rf"R^2(C_{{t-{window}+1:t}}\sim\mathrm{{time}})",
        "ROC": rf"\frac{{C_{{t-{window}}}}}{{C_t}}", "MA": rf"\frac{{\operatorname{{Mean}}_{{{window}}}(C_t)}}{{C_t}}",
        "MAX": rf"\frac{{\operatorname{{Max}}_{{{window}}}(H_t)}}{{C_t}}", "MIN": rf"\frac{{\operatorname{{Min}}_{{{window}}}(L_t)}}{{C_t}}",
        "QTLU": rf"\frac{{Q^{{80\%}}_{{{window}}}(C_t)}}{{C_t}}", "QTLD": rf"\frac{{Q^{{20\%}}_{{{window}}}(C_t)}}{{C_t}}",
        "RANK": rf"\operatorname{{PercentileRank}}\!\left(C_t;C_{{t-{window}+1:t}}\right)",
        "IMAX": rf"\frac{{\operatorname{{argmax}}_{{{window}}}(H)+1}}{{{window}}}", "IMIN": rf"\frac{{\operatorname{{argmin}}_{{{window}}}(L)+1}}{{{window}}}",
        "IMXD": rf"\frac{{\operatorname{{argmax}}_{{{window}}}(H)-\operatorname{{argmin}}_{{{window}}}(L)}}{{{window}}}",
        "RSV": rf"\frac{{C_t-\operatorname{{Min}}_{{{window}}}(L)}}{{\operatorname{{Max}}_{{{window}}}(H)-\operatorname{{Min}}_{{{window}}}(L)}}",
        "CNTP": rf"\operatorname{{Mean}}_{{{window}}}\!\left(\mathbf 1[C_t>C_{{t-1}}]\right)",
        "CNTN": rf"\operatorname{{Mean}}_{{{window}}}\!\left(\mathbf 1[C_t<C_{{t-1}}]\right)",
        "CNTD": rf"\operatorname{{Mean}}_{{{window}}}(\mathbf 1[C_t>C_{{t-1}}])-\operatorname{{Mean}}_{{{window}}}(\mathbf 1[C_t<C_{{t-1}}])",
        "SUMP": rf"\frac{{\sum_{{{window}}}\max(\Delta C_t,0)}}{{\sum_{{{window}}}|\Delta C_t|}}", "SUMN": rf"\frac{{\sum_{{{window}}}\max(-\Delta C_t,0)}}{{\sum_{{{window}}}|\Delta C_t|}}",
        "SUMD": rf"\frac{{\sum_{{{window}}}\max(\Delta C_t,0)-\sum_{{{window}}}\max(-\Delta C_t,0)}}{{\sum_{{{window}}}|\Delta C_t|}}",
        "VMA": rf"\frac{{\operatorname{{Mean}}_{{{window}}}(V_t)}}{{V_t}}", "VSUMP": rf"\frac{{\sum_{{{window}}}\max(\Delta V_t,0)}}{{\sum_{{{window}}}|\Delta V_t|}}",
        "VSUMN": rf"\frac{{\sum_{{{window}}}\max(-\Delta V_t,0)}}{{\sum_{{{window}}}|\Delta V_t|}}", "VSUMD": rf"\frac{{\sum_{{{window}}}\max(\Delta V_t,0)-\sum_{{{window}}}\max(-\Delta V_t,0)}}{{\sum_{{{window}}}|\Delta V_t|}}",
        "CORR": rf"\operatorname{{Corr}}_{{{window}}}\!\left(C_t,\ln(V_t+1)\right)",
        "CORD": rf"\operatorname{{Corr}}_{{{window}}}\!\left(\frac{{C_t}}{{C_{{t-1}}}},\ln\!\left(\frac{{V_t}}{{V_{{t-1}}}}+1\right)\right)",
        "STD": rf"\frac{{\operatorname{{Std}}_{{{window}}}(C_t)}}{{C_t}}", "VSTD": rf"\frac{{\operatorname{{Std}}_{{{window}}}(V_t)}}{{V_t}}",
        "WVMA": rf"\frac{{\operatorname{{Std}}_{{{window}}}(|r_t|V_t)}}{{\operatorname{{Mean}}_{{{window}}}(|r_t|V_t)}}",
    }
    if operation not in formulas:
        definition = _public_factor_formula(factor_name, config)
        if definition is not None:
            return definition
        raise ValueError(f"因子 {factor_name} 缺少可核验的数学公式")
    return formulas[operation]


def factor_direction(ic_mean: float) -> str:
    """仅按2020年以来未舍入的中性化每日IC均值确定方向。"""
    if not np.isfinite(ic_mean) or ic_mean == 0:
        return "无法判定"
    return "正向" if ic_mean > 0 else "负向"


def weekly_ic_statistics(ic_series: pd.Series,
                         full_period_ic_mean: float = np.nan) -> dict[str, Any]:
    values = pd.to_numeric(ic_series,errors="coerce").replace([np.inf,-np.inf],np.nan).dropna().sort_index()
    values.index = pd.to_datetime(values.index)
    weekly = values.groupby(values.index.to_period("W-SUN")).mean()
    reference = np.sign(full_period_ic_mean) if np.isfinite(full_period_ic_mean) else 0
    if weekly.empty or reference == 0:
        return {"sign":"~","week_count":len(weekly),"win_rate":np.nan,
                "autocorrelation":np.nan,"max_failure_streak":np.nan,"failure_interval":"~"}
    failures = weekly*reference <= 0
    streaks = [group for _,group in failures.groupby(failures.ne(failures.shift()).cumsum()) if group.iloc[0]]
    longest = max(streaks,key=len) if streaks else pd.Series(dtype=bool)
    failed_dates=values.index[values.index.to_period("W-SUN").isin(longest.index)]
    interval = f"{failed_dates.min().date()} 至 {failed_dates.max().date()}" if len(failed_dates) else "无"
    return {"sign":"+" if reference>0 else "-","week_count":len(weekly),
            "win_rate":float((weekly*reference>0).mean()),
            "autocorrelation":float(weekly.autocorr()) if len(weekly)>2 else np.nan,
            "max_failure_streak":len(longest),"failure_interval":interval}


def quintile_monotonicity(total_returns: list[float] | np.ndarray) -> float:
    """图片公式 M_new=abs(Kendall tau)*abs(Spearman rho)，无并列时等价于平方名次偏差式。"""
    values = np.asarray(total_returns,dtype=float)
    if values.shape!=(5,) or not np.isfinite(values).all():
        return np.nan
    if np.ptp(values)==0:
        return 0.0
    order = np.arange(1,6)
    # 并列收益采用平均秩和tau-b；避免任意证券/分组顺序制造单调性。
    tau = float(stats.kendalltau(order,values,variant="b").statistic)
    rho = float(stats.spearmanr(order,values).statistic)
    return float(abs(tau)*abs(rho))


def interval_return(returns: pd.Series) -> float:
    values = pd.to_numeric(returns,errors="coerce").dropna()
    return float((1+values).prod()-1) if len(values) else np.nan


def max_drawdown(returns: pd.Series) -> float:
    values = pd.to_numeric(returns,errors="coerce").dropna()
    if values.empty:return np.nan
    # 必须纳入区间期初净值1，否则遗漏首期亏损。
    nav = np.r_[1.0,(1+values).cumprod().to_numpy()]
    return float(np.min(nav/np.maximum.accumulate(nav)-1))


def number(value: Any, digits: int = 4) -> str:
    try:v=float(value)
    except (TypeError,ValueError):return "~" if value is None else str(value)
    return f"{v:.{digits}f}" if np.isfinite(v) else "~"


def percent(value: Any) -> str:
    try:v=float(value)
    except (TypeError,ValueError):return "~"
    return f"{v:.2%}" if np.isfinite(v) else "~"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    def escape(v):return str(v).replace('|',r'\|').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(map(escape,headers))+' |',
                      '|'+'|'.join('---' for _ in headers)+'|',
                      *['| '+' | '.join(map(escape,row))+' |' for row in rows]])


def _html_inline(value: str) -> str:
    # 只解析本报告生成器使用的行内语法，所有数据先做HTML转义。
    escaped=html.escape(value.replace(r'\|','|'))
    escaped=re.sub(r'`([^`]+)`',r'<code>\1</code>',escaped)
    escaped=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',escaped)
    return escaped.replace('&lt;br&gt;','<br>')


def report_directory(value_directory: Path) -> Path:
    """报告与因子值、IC、收益目录并列，不写入因子值目录。"""
    value_directory = Path(value_directory)
    return value_directory.parent.parent / 'factor_report' / value_directory.name


def validate_report_config(factor_name: str, config: dict[str, Any]) -> None:
    """计算前检查报告必需的解释和公式，不等全量计算后才发现遗漏。"""
    description = config.get('description')
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f'{factor_name}缺少非空配置description，不能完成报告流程')
    if not factor_formula(factor_name, config).strip():
        raise ValueError(f'{factor_name}缺少完整公式定义，不能完成报告流程')


def return_curve_data(returns: pd.DataFrame, core_metrics: dict[str, Any],
                      metadata: dict[str, Any], universe_name: str) -> dict[str, Any]:
    """图表只复用精细账户周收益；不得补零或从IC标签重构组合收益。"""
    benchmark_code = metadata.get('source_paths', {}).get('benchmark_index')
    if not benchmark_code:
        raise ValueError('收益来源缺少benchmark_index，不能给曲线标注大盘')
    expected_code = {'中证500': '000905.SH', '中证1000': '000852.SH'}.get(universe_name)
    if expected_code is not None and benchmark_code != expected_code:
        raise ValueError(f'报告股票池{universe_name}与收益基准{benchmark_code}不一致')
    result = {'benchmark': f'{universe_name}（{benchmark_code}）', 'versions': {}}
    benchmark_frames = []
    years = set()
    for version, prefix in (('raw', 'raw:'), ('neutralization', '')):
        frames = []
        for side in ('top_20', 'bottom_20'):
            frame = returns.loc[returns.portfolio.eq(prefix + side)].copy()
            if frame.empty or frame.week_id.duplicated().any():
                raise ValueError(f'{version}:{side}曲线数据缺失或自然周重复')
            frame = frame.sort_values('week_first_trade').set_index('week_id')
            frames.append(frame)
        top, bottom = frames
        if not top.index.equals(bottom.index):
            raise ValueError(f'{version}的Top20和Bottom20自然周不一致')
        dates = ['week_first_trade', 'week_last_trade']
        if not top[dates].equals(bottom[dates]) or top[dates].isna().any().any():
            raise ValueError(f'{version}的Top20和Bottom20日期不一致或缺失')
        if (top.week_first_trade > top.week_last_trade).any():
            raise ValueError(f'{version}的自然周日期范围错误')
        values = np.column_stack((top.weekly_return, bottom.weekly_return, top.benchmark_return)).astype(float)
        if not np.isfinite(values).all() or (values < -1).any():
            raise ValueError(f'{version}收益曲线包含非法收益，不能绘图')
        if not np.allclose(top.benchmark_return, bottom.benchmark_return, rtol=0, atol=1e-12):
            raise ValueError(f'{version}的Top20和Bottom20基准收益不一致')
        if not np.isfinite(np.cumprod(1 + values, axis=0)).all():
            raise ValueError(f'{version}累计收益溢出，不能绘图')
        benchmark_frames.append(top.benchmark_return)
        rows = [[first.strftime('%Y-%m-%d'), last.strftime('%Y-%m-%d'), *numbers]
                for first, last, numbers in zip(top.week_first_trade, top.week_last_trade, values.tolist())]
        mean = core_metrics[version]['IC_mean']
        mean = float(mean) if mean is not None and np.isfinite(mean) else None
        result['versions'][version] = {
            'ic_mean': mean,
            'oriented': 'top' if mean is not None and mean > 0 else ('bottom' if mean is not None and mean < 0 else None),
            'weeks': rows,
        }
        years.update(first[:4] for first, last, *_ in rows if first[:4] == last[:4])
    left, right = benchmark_frames
    common = left.index.intersection(right.index)
    if len(common) and not np.allclose(left.loc[common], right.loc[common], rtol=0, atol=1e-12):
        raise ValueError('原始和中性化版本的基准收益不一致')
    result['years'] = sorted(years)
    return result


_RETURN_CHART_STYLE = '''
main{overflow-wrap:anywhere}
.curve-heading{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}.curve-heading h2{margin:0;border:0;padding:12px 0}.curve-heading label{color:var(--muted)}.curve-heading select{margin-left:10px;padding:7px 12px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink);font:inherit}.curve-card{border:1px solid var(--line);border-radius:10px;background:var(--card);padding:16px;margin:16px 0}.curve-card h3{margin:0 0 12px}.curve-layout{display:grid;grid-template-columns:minmax(0,1fr) 245px;gap:18px;align-items:start}.curve-plot{position:relative;min-width:0}.curve-plot svg{display:block;width:100%;height:auto;touch-action:pan-y}.curve-side{padding:12px;background:var(--bg);border-radius:7px;font-variant-numeric:tabular-nums}.curve-direction{font-weight:650;font-size:15px}.curve-ic,.curve-range{color:var(--muted);font-size:12px;margin:7px 0 14px;overflow-wrap:anywhere}.curve-legend{display:grid;gap:10px}.curve-legend div{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.curve-swatch{width:20px;height:3px;display:inline-block;flex:none}.curve-legend strong{margin-left:auto}.curve-tooltip{position:absolute;pointer-events:none;padding:9px 12px;background:#060d1cf0;border:1px solid var(--line);border-radius:6px;font-size:12px;white-space:pre-line;z-index:2}.curve-note{color:var(--muted);font-size:12px}.curve-empty{color:var(--muted)}@media(max-width:850px){.curve-layout{grid-template-columns:1fr}.curve-side{display:block}.curve-legend{grid-template-columns:repeat(3,minmax(0,1fr))}.curve-legend strong{margin-left:0}}@media(max-width:480px){.curve-legend{grid-template-columns:1fr}}
'''


_RETURN_CHART_SCRIPT = r'''
(() => {
 const source=document.getElementById('return-curve-data');
 if(!source)return;
 const data=JSON.parse(source.textContent),select=document.getElementById('curve-period');
 const colors={top:'#65b7ff',bottom:'#fb923c',benchmark:'#c4b5fd'};
 const labels={top:'Top20%',bottom:'Bottom20%',benchmark:data.benchmark};
 const keys=['top','bottom','benchmark'],NS='http://www.w3.org/2000/svg';
 const percent=v=>(v*100).toLocaleString('zh-CN',{minimumFractionDigits:2,maximumFractionDigits:2})+'%';
 const timestamp=s=>Date.parse(s+'T00:00:00Z');
 function element(tag,attrs={},text){const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;}
 for(const year of data.years){const option=document.createElement('option');option.value=year;option.textContent=year+'年';select.append(option);}
 function draw(card){
  const version=data.versions[card.dataset.version],year=select.value;
  const weeks=version.weeks.filter(r=>year==='all'||(r[0].slice(0,4)===year&&r[1].slice(0,4)===year));
  const svg=card.querySelector('svg'),tooltip=card.querySelector('.curve-tooltip'),range=card.querySelector('.curve-range');
  svg.replaceChildren();tooltip.hidden=true;svg.onpointermove=null;svg.onpointerleave=null;
  svg.dataset.period=year;svg.dataset.weeks=String(weeks.length);
  const chosen=version.oriented==='top'?'Top20%':(version.oriented==='bottom'?'Bottom20%':'无法判定');
  card.querySelector('.curve-direction').textContent='正向化组合：'+chosen;
  card.querySelector('.curve-ic').textContent='全时段 IC_mean：'+(version.ic_mean===null?'无有效值':Number(version.ic_mean).toPrecision(6))+'；切换年份不改变方向';
  if(!weeks.length){range.textContent='该区间没有完整自然周';svg.append(element('text',{x:80,y:70,fill:'#9aaac4'},'该区间没有完整自然周，未补造收益'));card.querySelector('.curve-legend').replaceChildren();return;}
  const times=[timestamp(weeks[0][0]),...weeks.map(r=>timestamp(r[1]))],dates=[weeks[0][0],...weeks.map(r=>r[1])];
  const series={top:[0],bottom:[0],benchmark:[0]};
  for(const row of weeks)for(const [j,key] of keys.entries())series[key].push((1+series[key].at(-1))*(1+row[j+2])-1);
  const W=1000,H=390,L=85,R=20,T=20,B=48;
  const values=keys.flatMap(k=>series[k]),lo=Math.min(0,...values),hi=Math.max(0,...values);
  const pad=(hi-lo||0.02)*0.10,minY=lo-pad,maxY=hi+pad;
  const x=t=>L+(t-times[0])/(times.at(-1)-times[0]||1)*(W-L-R),y=v=>T+(maxY-v)/(maxY-minY)*(H-T-B);
  svg.append(element('title',{},card.querySelector('h3').textContent+'，'+dates[0]+'至'+dates.at(-1)+'，累计收益率'));
  for(let j=0;j<=5;j++){const value=minY+(maxY-minY)*j/5,py=y(value);svg.append(element('line',{x1:L,x2:W-R,y1:py,y2:py,stroke:'#263750'}));svg.append(element('text',{x:L-10,y:py+4,'text-anchor':'end',fill:'#9aaac4','font-size':12},percent(value)));}
  svg.append(element('line',{x1:L,x2:W-R,y1:y(0),y2:y(0),stroke:'#708099','stroke-dasharray':'4 4'}));
  for(let j=0;j<=4;j++){const i=Math.round((dates.length-1)*j/4);svg.append(element('text',{x:x(times[i]),y:H-18,'text-anchor':j===0?'start':(j===4?'end':'middle'),fill:'#9aaac4','font-size':12},dates[i]));}
  const legend=card.querySelector('.curve-legend');legend.replaceChildren();
  for(const key of keys){
   const path=element('path',{d:series[key].map((v,i)=>(i?'L':'M')+x(times[i]).toFixed(2)+','+y(v).toFixed(2)).join(' '),fill:'none',stroke:colors[key],'stroke-width':key===version.oriented?2.6:1.8,'data-series':key,'data-final-return':series[key].at(-1)});svg.append(path);
   const row=document.createElement('div'),swatch=document.createElement('span'),label=document.createElement('span'),value=document.createElement('strong');swatch.className='curve-swatch';swatch.style.background=colors[key];label.textContent=labels[key];value.textContent=percent(series[key].at(-1));row.append(swatch,label,value);legend.append(row);
  }
  range.textContent=dates[0]+' 至 '+dates.at(-1)+' · '+weeks.length+'个完整自然周';
  const cursor=element('line',{x1:L,x2:L,y1:T,y2:H-B,stroke:'#dce7f5','stroke-dasharray':'3 3',visibility:'hidden'});svg.append(cursor);
  svg.onpointermove=event=>{
   const rect=svg.getBoundingClientRect(),px=(event.clientX-rect.left)/rect.width*W;
   if(px<L||px>W-R){tooltip.hidden=true;cursor.setAttribute('visibility','hidden');return;}
   let index=0,distance=Infinity;for(let i=0;i<times.length;i++){const d=Math.abs(x(times[i])-px);if(d<distance){index=i;distance=d;}}
   cursor.setAttribute('x1',x(times[index]));cursor.setAttribute('x2',x(times[index]));cursor.setAttribute('visibility','visible');
   tooltip.textContent=dates[index]+(index===0?' · 期初基准':' · 周末')+'\n'+keys.map(k=>labels[k]+'：'+percent(series[k][index])).join('\n');tooltip.hidden=false;
   const box=card.querySelector('.curve-plot').getBoundingClientRect();tooltip.style.left=Math.max(0,Math.min(event.clientX-box.left+12,box.width-tooltip.offsetWidth))+'px';tooltip.style.top=Math.max(0,event.clientY-box.top-tooltip.offsetHeight-10)+'px';
  };
  svg.onpointerleave=()=>{tooltip.hidden=true;cursor.setAttribute('visibility','hidden');};
 }
 const cards=[...document.querySelectorAll('.curve-card')];select.addEventListener('change',()=>cards.forEach(draw));cards.forEach(draw);
})();
'''


def _return_chart_html(curves: dict[str, Any]) -> str:
    cards = ''.join(
        f'<article class="curve-card" data-version="{key}"><h3>{label}</h3>'
        '<div class="curve-layout"><div class="curve-plot">'
        f'<svg viewBox="0 0 1000 390" role="img" aria-label="{label}累计收益曲线"></svg>'
        '<div class="curve-tooltip" hidden></div></div><aside class="curve-side">'
        '<div class="curve-direction"></div><div class="curve-ic"></div>'
        '<div class="curve-legend"></div><div class="curve-range"></div></aside></div></article>'
        for key, label in (('raw', '原始因子值（Raw factor）'), ('neutralization', '中性化因子值（Neutralized factor）')))
    payload = json.dumps(curves, ensure_ascii=False, allow_nan=False, separators=(',', ':')).replace('<', r'\u003c')
    return ('<section id="return-curves"><div class="curve-heading"><h2>累计收益曲线（Cumulative return）</h2>'
            '<label for="curve-period">展示区间<select id="curve-period"><option value="all">全时段</option></select></label></div>'
            '<p class="curve-note">按完整自然周净收益复利，周末采样。区间期初为0%，年度展示沿用原账户路径，不重新建仓；'
            '年度仅纳入起止交易日均在该年内的完整周。正向化方向始终参考对应版本的全时段IC均值；IC为0或无有效值时不指定方向。</p>'
            + cards + '<noscript>交互曲线需要启用JavaScript，下面的报告表格仍可直接阅读。</noscript></section>'
            + '<script id="return-curve-data" type="application/json">' + payload + '</script>')


def markdown_to_html(markdown: str, curves: dict[str, Any] | None = None) -> str:
    """表格从MD转换，交互曲线使用同一份精细账户周收益，全部内嵌且可离线打开。"""
    lines=markdown.splitlines(); blocks=[];position=0
    while position<len(lines):
        line=lines[position]
        if not line.strip():position+=1;continue
        if line.startswith('|') and position+1<len(lines) and re.fullmatch(r'[|:\- ]+',lines[position+1]):
            table=[]
            while position<len(lines) and lines[position].startswith('|'):
                cells=[c.strip() for c in re.split(r'(?<!\\)\|',lines[position].strip('|'))]
                table.append(cells);position+=1
            headers=table[0]
            body=''.join('<tr>'+''.join('<td>'+_html_inline(c)+'</td>' for c in row)+'</tr>' for row in table[2:])
            blocks.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+_html_inline(c)+'</th>' for c in headers)+'</tr></thead><tbody>'+body+'</tbody></table></div>')
            continue
        heading=re.match(r'^(#{1,6}) (.+)$',line)
        if heading:
            level=len(heading[1]);blocks.append(f'<h{level}>'+_html_inline(heading[2])+f'</h{level}>')
        elif line.startswith('> '):blocks.append('<blockquote>'+_html_inline(line[2:])+'</blockquote>')
        elif line.startswith('- '):blocks.append('<p class="method">'+_html_inline(line[2:])+'</p>')
        else:blocks.append('<p>'+_html_inline(line)+'</p>')
        position+=1
    source=json.dumps(markdown,ensure_ascii=False).replace('<',r'\u003c')
    title=html.escape(lines[0].removeprefix('# '))
    content=''.join(blocks)
    if curves is not None:
        content=content.replace('</h1>', '</h1>'+_return_chart_html(curves), 1)
    return '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+'''</title><style>
:root{color-scheme:dark;--bg:#0b1120;--card:#111c30;--ink:#e4eaf4;--muted:#9aaac4;--line:#263750;--accent:#65b7ff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}main{max-width:1600px;margin:auto;padding:30px 28px 64px}h1{font-size:27px;margin:8px 0 16px}h2{color:var(--accent);border-bottom:1px solid var(--line);padding:22px 0 8px;margin-top:28px}h3{margin-top:26px}blockquote{margin:16px 0;padding:12px 16px;border-left:3px solid var(--accent);background:var(--card);color:var(--muted)}.table-wrap{max-width:100%;overflow:auto;border:1px solid var(--line);border-radius:8px;margin:10px 0 24px}table{border-collapse:collapse;min-width:100%;font-variant-numeric:tabular-nums}th,td{padding:9px 12px;border:1px solid var(--line);text-align:right;white-space:nowrap}th{background:#192a44;position:sticky;top:0;cursor:pointer}td:first-child,th:first-child{text-align:left}tbody tr:nth-child(even){background:var(--card)}code{font-size:13px;color:#b6d6f7}.method{color:var(--muted);margin:7px 0}button{padding:7px 12px;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:6px;cursor:pointer}@media(max-width:700px){main{padding:16px 12px}h1{font-size:22px}}
</style><style>'''+_RETURN_CHART_STYLE+'''</style></head><body><main>'''+content+'''</main><script id="markdown-source" type="application/json">'''+source+'''</script><script>
for(const table of document.querySelectorAll('table'))for(const [col,th] of [...table.tHead.rows[0].cells].entries())th.onclick=()=>{const body=table.tBodies[0],rows=[...body.rows],dir=th.dataset.dir==='1'?-1:1;th.dataset.dir=String(dir);rows.sort((a,b)=>{const x=a.cells[col].textContent.trim(),y=b.cells[col].textContent.trim(),nx=parseFloat(x),ny=parseFloat(y);return dir*(Number.isFinite(nx)&&Number.isFinite(ny)?nx-ny:x.localeCompare(y,'zh-CN',{numeric:true}));});rows.forEach(row=>body.append(row));};
</script><script>'''+_RETURN_CHART_SCRIPT+'''</script></body></html>'''


def _ic_summary(ic: pd.Series, horizon: int = 5) -> dict[str,float]:
    result=calc_offset_ic_stats(ic,horizon)
    t,p=calc_t_stat(ic,horizon);result.update(t_stat=t,p_value=p)
    return result


def build_factor_report(runner: Any, signal_versions: dict[str,pd.DataFrame],
                        factor_config: dict[str,Any], return_dir: Path | None = None) -> Path:
    """收益完成后独立保存MD/HTML，HTML另含双版本交互收益曲线。"""
    validate_report_config(runner.factor_name, factor_config)
    value_dir=Path(runner.output_dir)
    output_dir=Path(getattr(runner, 'report_output_dir', report_directory(value_dir)))
    return_dir=Path(return_dir or getattr(runner,'return_output_dir',
        value_dir.parents[1]/'factor_return'/runner.factor_name))
    meta_path=return_dir/'report_return_metadata.json'
    returns_path=return_dir/'report_portfolios.parquet'
    if not meta_path.is_file() or not returns_path.is_file():
        raise FileNotFoundError(f'必须先通过return_engine.py完成报告全部组合回测: {return_dir}')
    metadata=json.loads(meta_path.read_text())
    if metadata.get('status')!='completed':raise ValueError('精细回测尚未完成')
    import return_engine
    if (metadata.get('engine_version')!=return_engine.ENGINE_VERSION or
        metadata.get('engine_sha256')!=hashlib.sha256(Path(return_engine.__file__).read_bytes()).hexdigest()):
        raise ValueError('精细收益的引擎版本或代码签名已改变，须先重算收益')
    factor_frame=getattr(runner,'report_factor_frame',None)
    if factor_frame is None:factor_frame=read_factor_output(value_dir,'neutralization')
    current_hash=hashlib.sha256(pd.util.hash_pandas_object(factor_frame,index=True).values.tobytes()).hexdigest()
    if metadata.get('signature',{}).get('neutralized_factor_hash')!=current_hash:
        raise ValueError('精细收益与当前中性化因子值版本不同，不能拼接报告')
    raw_frame=getattr(runner,'report_raw_factor_frame',None)
    if raw_frame is None:raw_frame=read_factor_output(value_dir,'raw')
    raw_hash=hashlib.sha256(pd.util.hash_pandas_object(raw_frame,index=True).values.tobytes()).hexdigest()
    if metadata.get('signature',{}).get('raw_factor_hash')!=raw_hash:
        raise ValueError('精细收益与当前原始因子值版本不同，不能拼接报告')
    start=max(REPORT_START,pd.Timestamp(metadata['requested_start']))
    end=pd.Timestamp(metadata['requested_end'])
    if end>REPORT_END and not getattr(runner,'allow_later_report_end',False):
        raise ValueError('当前已确认因子有效截止日为2026-06-30，不能纳入后续数据')
    data=runner.data.loc[runner.data.index.get_level_values('date').to_series(index=runner.data.index).between(start,end)]
    if data.empty:raise ValueError('2020年以来没有有效报告行情')
    signals=signal_versions['neutralization'].sort_index()
    panel=signals.reindex(index=pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values())
    returns=pd.read_parquet(returns_path)
    returns=returns.loc[(returns.week_first_trade>=start)&(returns.week_last_trade<=end)]
    if returns.empty:raise ValueError('报告区间没有精细回测收益')
    forward_panels=getattr(runner,'report_forward_returns',{})
    ic_series={}
    for horizon in IC_DECAY_PERIODS:
        target=forward_panels.get(horizon)
        if target is None:target=calc_forward_returns(data,horizon,price_col=runner.eval_price_col).unstack('symbol')
        target=target.loc[target.index.to_series().between(start,end)]
        ic_series[horizon]=calc_ic_panel(panel,target,runner.ic_method)
    ic=ic_series[5];core=_ic_summary(ic);ic_mean=core['IC_mean']
    weekly=weekly_ic_statistics(ic,full_period_ic_mean=ic_mean)
    recent_start=(end.to_period('M')-2).start_time
    def subset(key,lower=start,upper=end,version='neutralization'):
        key=key if version=='neutralization' else version+':'+key
        return returns.loc[(returns.portfolio==key)&(returns.week_first_trade>=lower)&(returns.week_last_trade<=upper)].sort_values('week_first_trade')
    def portfolio_stats(key,lower=start,upper=end,version='neutralization'):
        frame=subset(key,lower,upper,version)
        if frame.empty:return (np.nan,np.nan,np.nan)
        total=interval_return(frame.weekly_return)
        excess=interval_return((1+frame.weekly_return)/(1+frame.benchmark_return)-1)
        return total,excess,max_drawdown(frame.weekly_return)
    group_keys=['bottom_20','quintile_2','quintile_3','quintile_4','top_20']
    full_groups=[portfolio_stats(k)[0] for k in group_keys]
    recent_groups=[portfolio_stats(k,recent_start)[0] for k in group_keys]
    group_dates=[set(subset(k).week_id) for k in group_keys]
    if any(d!=group_dates[0] for d in group_dates[1:]):
        raise ValueError('五分组有效自然周不一致，不能计算可比单调性')
    description=factor_config.get('description')
    if not description and factor_config.get('category')==MINUTE_CATEGORY:
        description=getattr(getattr(runner,'factor',None),'description',None)
    if not description:raise ValueError(f'{runner.factor_name}缺少配置description')
    valid_ic=ic.dropna()
    data_dates=pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values()
    factor_in_window=signals.loc[signals.index.to_series().between(start,end)]
    eligible=panel.stack(future_stack=True).reindex(data.index)
    missing=1-float(np.isfinite(eligible).sum())/len(eligible) if len(eligible) else np.nan
    formula = factor_config.get('formula') or _public_factor_formula(runner.factor_name, factor_config)
    if formula is None:
        formula = f'`${factor_formula(runner.factor_name, factor_config)}$`'
    rows=[['因子名称',runner.factor_name],['ID',factor_config.get('ID','~')],
          ['因子类别',factor_config.get('category','~')],['经济学解释',description],
          ['计算公式',formula],
          ['股票池',getattr(runner,'universe_name','中证500')+'历史成分股'],
          ['因子数据区间',f'{factor_in_window.index.min().date()} 至 {factor_in_window.index.max().date()}'],
          ['报告统计区间',f'{start.date()} 至 {end.date()}'],
          ['5日IC有效区间',f'{valid_ic.index.min().date()} 至 {valid_ic.index.max().date()}' if len(valid_ic) else '~'],
          ['精细收益有效区间',f'{subset("top_20").week_first_trade.min().date()} 至 {subset("top_20").week_last_trade.max().date()}'],
          ['中性化','对数市值＋申万一级行业OLS残差'],['空缺率',percent(missing)]]
    core_headers=['因子版本','IC均值','IC标准差','ICIR','t-stat','p-value','因子方向',
                  '自然周IC胜率','IC偏度','最大连续失效周数','最长失效区间','5日单边换手率',
                  '总时段正向化Top20收益','总时段正向化Top20最大回撤','总时段单调性得分',
                  '近3个月单调性得分','近3个月是否反向']
    core_rows=[]
    core_metrics={}
    raw_target=forward_panels.get(5)
    if raw_target is None:raw_target=calc_forward_returns(data,5,price_col=runner.eval_price_col).unstack('symbol')
    raw_target=raw_target.loc[raw_target.index.to_series().between(start,end)]
    for version,label in [('raw','原始因子值'),('neutralization','中性化因子值')]:
        version_ic=ic if version=='neutralization' else calc_ic_panel(signal_versions['raw'],raw_target,runner.ic_method)
        version_stats=core if version=='neutralization' else _ic_summary(version_ic)
        mean=version_stats['IC_mean']
        version_weekly=weekly_ic_statistics(version_ic,full_period_ic_mean=mean)
        chosen='top_20' if np.isfinite(mean) and mean>0 else ('bottom_20' if np.isfinite(mean) and mean<0 else None)
        groups=[portfolio_stats(k,version=version)[0] for k in group_keys]
        recent=[portfolio_stats(k,recent_start,version=version)[0] for k in group_keys]
        dates=[set(subset(k,version=version).week_id) for k in group_keys]
        if not dates[0] or any(d!=dates[0] for d in dates[1:]):
            raise ValueError(f'{version}五分组缺失或有效自然周不一致，不能计算单调性')
        oriented=portfolio_stats(chosen,version=version) if chosen else (np.nan,np.nan,np.nan)
        trades=subset(chosen,version=version) if chosen else pd.DataFrame()
        turnover=float(trades.one_way_turnover.mean()) if not trades.empty else np.nan
        reverse='无法判定'
        if chosen and np.isfinite(recent[-1]) and np.isfinite(recent[0]):
            reverse='是' if (mean>0 and recent[-1]<recent[0]) or (mean<0 and recent[-1]>recent[0]) else '否'
        monotonicity=quintile_monotonicity(groups)
        recent_monotonicity=quintile_monotonicity(recent)
        core_rows.append([label,number(mean,6),number(version_stats['IC_std'],6),number(version_stats['ICIR']),
            number(version_stats['t_stat']),number(version_stats['p_value'],6),factor_direction(mean),
            percent(version_weekly['win_rate']),number(version_ic.dropna().skew()),version_weekly['max_failure_streak'],
            version_weekly['failure_interval'],percent(turnover),percent(oriented[0]),percent(oriented[2]),
            number(monotonicity),number(recent_monotonicity),reverse])
        core_metrics[version]={'IC_mean':mean if np.isfinite(mean) else None,
            'monotonicity_total':monotonicity if np.isfinite(monotonicity) else None,
            'monotonicity_recent':recent_monotonicity if np.isfinite(recent_monotonicity) else None,
            'recent_reversed':reverse}
    sections=[f'# {runner.factor_name} 单因子验收与评估报告',
              '> 核心指标保留原始因子值（Raw factor）和中性化因子值（Neutralized factor）；其余结果仅使用中性化值。全部组合收益使用 return_engine.py 精细账户回测。',
              '## 一、基本信息',markdown_table(['项目','内容'],rows),
              '## 二、核心指标',markdown_table(core_headers,core_rows),'## 三、细节表现',
              '### 自相关及双向组合表现',markdown_table(['IC滞后1期自相关系数','Top20区间绝对收益',
                  'Bottom20区间绝对收益','Top20绝对最大回撤','Bottom20绝对最大回撤'],
                  [[number(weekly['autocorrelation']),percent(full_groups[-1]),percent(full_groups[0]),
                    percent(portfolio_stats('top_20')[2]),percent(portfolio_stats('bottom_20')[2])]]),
              '### IC衰减']
    decay_stats={h:_ic_summary(ic_series[h],h) for h in IC_DECAY_PERIODS}
    sections.append(markdown_table(['持有期','中性化IC均值','中性化ICIR','中性化p值'],
                    [[f'{h}日',number(s['IC_mean'],6),number(s['ICIR']),number(s['p_value'],6)] for h,s in decay_stats.items()]))
    strengths={h:abs(s['IC_mean']) for h,s in decay_stats.items() if np.isfinite(s['IC_mean'])}
    peak=max(strengths,key=strengths.get) if strengths else None
    half='~' if peak is None else '>60'
    if peak is not None:
        for h in sorted(k for k in strengths if k>peak):
            if all(strengths[k]<=strengths[peak]/2 for k in strengths if k>=h):half=str(h-peak);break
    sections += ['#### 衰减结论',markdown_table(['IC峰值持有期','峰值IC强度','IC半衰期（交易日）'],
        [[f'{peak}日' if peak else '~',number(strengths.get(peak,np.nan)),half]]),
        '### 五分组表现',markdown_table(['分组','区间绝对收益','区间超额收益','绝对最大回撤','近3个月区间绝对收益'],
        [[f'Group {g}',*[percent(v) for v in portfolio_stats(key)],percent(recent_groups[g-1])] for g,key in enumerate(group_keys,1)]),
        '### Top/Bottom阈值表现',markdown_table(['组合','区间绝对收益','区间超额收益','绝对最大回撤'],
        [[f'{side.title()}{pct}%',*[percent(v) for v in portfolio_stats(f'{side}_{pct}')]]
         for pct in (10,20,30) for side in ('top','bottom')]),'### 滞后检验']
    lag_rows=[]
    target=forward_panels.get(5)
    if target is None:target=calc_forward_returns(data,5,price_col=runner.eval_price_col).unstack('symbol')
    target=target.loc[target.index.to_series().between(start,end)]
    for lag in range(4):
        lag_ic=ic if not lag else calc_ic_panel(signals.shift(lag).reindex(panel.index),target,runner.ic_method)
        lag_mean=float(lag_ic.mean())
        keys=['top_20','bottom_20'] if not lag else [f'lag_{lag}:{s}_20' for s in ('top','bottom')]
        lag_rows.append([lag,number(lag_mean,6),percent(abs(lag_mean)/abs(ic_mean) if ic_mean else np.nan),
                         *[percent(v) for key in keys for v in portfolio_stats(key)[:2]]])
    sections.append(markdown_table(['滞后交易日','IC均值','IC强度保留率','Top20区间绝对收益',
        'Top20区间超额收益','Bottom20区间绝对收益','Bottom20区间超额收益'],lag_rows))
    cap=data['total_mv'].unstack('symbol').reindex_like(panel)
    constituents=getattr(runner.data_loader,'constituents',pd.DataFrame())
    if not constituents.empty:
        cap=cap.where(constituents.reindex(index=cap.index,columns=cap.columns,fill_value=False))
    security_status=getattr(runner.data_loader,'security_status',pd.DataFrame())
    if not security_status.empty:
        cap=cap.where(~security_status.reindex(index=cap.index,columns=cap.columns,fill_value=False))
    ranks=cap.rank(axis=1,pct=True,method='first')
    buckets={'size_small':ranks<=1/3,'size_middle':(ranks>1/3)&(ranks<=2/3),'size_large':ranks>2/3}
    size_names={'size_small':'内部小盘组','size_middle':'内部中盘组','size_large':'内部大盘组'}
    size_rows=[]
    for key,mask in buckets.items():
        bucket_ic=calc_ic_panel(panel.where(mask),target,runner.ic_method)
        size_rows.append([size_names[key],number(bucket_ic.mean(),6),
            *[percent(v) for side in ('top','bottom') for v in portfolio_stats(key+':'+side+'_20')[:2]]])
    sections += ['## 四、市值表现',markdown_table(['市值层','IC均值','Top20区间绝对收益',
        'Top20区间超额收益','Bottom20区间绝对收益','Bottom20区间超额收益'],size_rows),'## 五、行业表现']
    industry=data['industry_sw_1'].unstack('symbol').reindex_like(panel)
    industry_rows=[]
    for name in sorted(str(v) for v in data['industry_sw_1'].dropna().unique() if str(v).strip()):
        mask=industry.eq(name);cols=mask.any(axis=0)
        industry_ic=calc_ic_panel(panel.loc[:,cols].where(mask.loc[:,cols]),target.loc[:,target.columns.intersection(panel.columns[cols])],runner.ic_method)
        win=weekly_ic_statistics(industry_ic,full_period_ic_mean=ic_mean)['win_rate']
        industry_rows.append([name,number(industry_ic.mean(),6),percent(win),
            *[percent(v) for side in ('top','bottom') for v in portfolio_stats('industry:'+name+':'+side+'_20')[:2]]])
    sections += [markdown_table(['行业','IC均值','自然周IC胜率','Top20区间绝对收益',
        'Top20区间超额收益','Bottom20区间绝对收益','Bottom20区间超额收益'],industry_rows),'## 六、年度表现']
    yearly=[];yearly_tails=[]
    calendar=data_dates
    label_end=pd.Series(calendar[6:].to_numpy(),index=calendar[:-6]) if len(calendar)>6 else pd.Series(dtype='datetime64[ns]')
    for year in range(start.year,end.year+1):
        first=max(start,pd.Timestamp(year,1,1));last=min(end,pd.Timestamp(year,12,31))
        year_ic=ic.loc[(ic.index>=first)&(ic.index<=last)]
        year_ic=year_ic.loc[label_end.reindex(year_ic.index).le(last).fillna(False)]
        summary=_ic_summary(year_ic);win=weekly_ic_statistics(year_ic,full_period_ic_mean=ic_mean)['win_rate']
        yearly.append([year,*[number(summary[k],6 if k in ('IC_mean','IC_std','p_value') else 4) for k in ('IC_mean','IC_std','ICIR','t_stat','p_value')],percent(win)])
        for pct in (10,20,30):
            for side in ('top','bottom'):
                yearly_tails.append([year,f'{side.title()}{pct}%',*[percent(v) for v in portfolio_stats(f'{side}_{pct}',first,last)]])
    sections += [markdown_table(['年份','IC均值','IC标准差','ICIR','t-stat','p-value','自然周IC胜率'],yearly),
                 '### 各自然年Top/Bottom阈值收益',markdown_table(['年份','组合','区间绝对收益','区间超额收益','绝对最大回撤'],yearly_tails),
                 '## 七、计算口径与数据来源',
                 f'- 全时段从{start.date()}至{end.date()}；近3个月为最近三个自然月（含截止日所在月）{recent_start.date()}至{end.date()}，仅使用起止交易日均落在区间内的完整自然周（Complete natural weeks）。',
                 '- IC是因子与T+1至T+6五日前向价格标签的横截面斯皮尔曼秩相关（Spearman rank correlation）；只保留在截止日前已完成标签的观测，标签收益只用于相关性，不作为组合回测收益。',
                 '- IC均值是有效逐日IC的等权算术均值，标准差使用样本标准差；ICIR=IC均值/IC标准差，显著性使用Newey-West异方差自相关稳健检验（HAC），5日标签使用4阶滞后。核心指标各行方向采用该版本未舍入的全时段IC均值；其他章节使用中性化IC方向，IC为零或缺失时不强行指定方向。',
                 '- 所有收益均为精细账户模拟的净收益（Net portfolio return），包括佣金、最低佣金、过户费、印花税、整手交易和现金约束，采用未复权实际成交价格；现引擎无独立滑点模型，滑点（Slippage）为0。',
                 '- 5日单边换手率核心指标各行使用该版本正向化组合每自然周实际成交金额之和/(2×调仓前权益)的均值；自然周通常为5个交易日，节假日短周按真实交易天数计算。',
                 '- 区间收益按自然周净收益复利计算；最大回撤（Maximum drawdown）由周末净值计算并纳入区间期初净值1，未使用日内或每日净值。年度和近3个月收益为同一连续账户路径内完整周收益的区间复利，不在每个子区间重新建仓。',
                 '- 核心指标各行五组按该版本未翻转的因子值从低到高划分，其他章节仅用中性化值；Group1与Bottom20、Group5与Top20完全一致，中间三组不重叠。尾部新买入20%、已有持仓仍在30%范围内保留；中间组新买入各20%，留仓范围向两侧各扩5个百分点，各组合独立模拟现金与交易费用。',
                 '- 单调性得分（Monotonicity score）按图片公式M_new=abs(Kendall tau)×abs(Spearman rho)；无并列时等价于M0×[1-min(D_up,D_down)/20]，M0=abs(tau)。并列收益采用平均秩和Kendall tau-b，五组完全同收益时得0，任一组缺失则不计算；绝对得分不区分正反向。',
                 '- 核心指标各行近3个月是否反向始终参考该版本全时段IC符号：正向因子Top20<Bottom20为反向，负向因子Top20>Bottom20为反向；收益相等为否，方向或收益缺失为无法判定。自然周IC胜率也采用全时段IC方向。',
                 '- IC滞后1期自相关系数按自然周IC均值序列计算1周滞后；自然周IC均值使用该周所有已完成前向标签的有效逐日IC，缺失值不补零。',
                 '- 行业、市值层的IC使用各层每日截面，精细组合在各层内排名；细分层无可交易组合时显示~，不回填零收益。',
                 '- 年度IC只纳入信号日及其前向标签结束日均在该自然年内的观测；IC衰减的各持有期使用各自已完成的标签区间，全部为中性化结果。',
                 f'- 精细收益来源：`{portable_path(returns_path)}`；参数和组合覆盖记录：`{portable_path(meta_path)}`。',
                 '- 经济学解释直接使用配置description；HTML由本份MD逐表逐段转换，内容和数值一致。']
    partial={k:(s['effective_start'],s['effective_end']) for k,s in metadata.get('portfolio_summaries',{}).items() if s.get('partial_coverage')}
    if partial:sections.append('- 部分细分组合实际有效区间：'+json.dumps(partial,ensure_ascii=False)+'。')
    if metadata.get('unavailable_portfolios'):sections.append('- 无有效细分组合：'+', '.join(metadata['unavailable_portfolios'])+'。')
    markdown=portable_payload('\n\n'.join(sections)+'\n')
    curves=return_curve_data(returns,core_metrics,metadata,getattr(runner,'universe_name','中证500'))
    html_content=markdown_to_html(markdown,curves)
    output_dir.mkdir(parents=True,exist_ok=True)
    path=output_dir/'factor_report.md'
    md_temp=path.with_suffix('.md.tmp');md_temp.write_text(markdown,encoding='utf-8');md_temp.replace(path)
    html_path=output_dir/'factor_report.html'
    html_temp=html_path.with_suffix('.html.tmp');html_temp.write_text(html_content,encoding='utf-8');html_temp.replace(html_path)
    return path

