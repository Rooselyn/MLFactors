#!/usr/bin/env python3
"""MLP v5增强版回测与年度交互式dashboard统一入口。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from dataloader import portable_payload, resolve_project_path, DEFAULT_TRADING_STATUS_PATH
from factors.registry import CATEGORY_NAMES
from dataloader import read_factor_output, read_weekly_output, write_output_parquet
INITIAL_CAPITAL = 1_000_000.0
MINIMUM_COVERAGE = 0.85
CATEGORY_LABELS = {english: chinese for chinese, english in CATEGORY_NAMES.items()}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def finite(value: float) -> float | None:
    number = float(value)
    return number if math.isfinite(number) else None

def load_engine():
    engine_path = PROJECT_ROOT / "return_engine.py"
    spec = importlib.util.spec_from_file_location("mlp_v5_return_engine", engine_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载收益引擎：{engine_path}")
    engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)
    return engine

def validate_sources() -> tuple[list[str], dict[str, int]]:
    if not SOURCE_ROOT.is_dir():
        raise FileNotFoundError(f"因子根目录不存在：{SOURCE_ROOT}")
    categories = sorted(
        path.name
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir() and (path / "raw.parquet").is_file()
    )
    expected = sorted(CATEGORY_LABELS)
    if categories != expected:
        raise ValueError(f"十类别不匹配：actual={categories}, expected={expected}")

    counts: dict[str, int] = {}
    for category in categories:
        frame = read_factor_output(SOURCE_ROOT / category, "raw")
        counts[category] = len(frame.columns) - 2
    return categories, counts

def load_return_report(directory: Path):
    metadata = json.loads((directory / "metadata.json").read_text())
    weekly = read_weekly_output(directory / "raw.parquet")
    weekly["benchmark_return"] = weekly.week_id.map(metadata["benchmark_weekly_returns"]["raw"])
    weekly.attrs["summary"] = {row["direction"]: row for row in metadata["summary"]["raw"]}
    return weekly, pd.DataFrame(metadata["summary"]["raw"])

def reusable_output(
    engine: Any,
    destination: Path,
    category: str,
    start: str,
    end: str,
) -> bool:
    if not engine.completed_factor_output(destination, category, versions=("raw",)):
        return False
    metadata = json.loads((destination / "metadata.json").read_text(encoding="utf-8"))
    return (
        metadata.get("requested_start") == start
        and metadata.get("requested_end") == end
        and resolve_project_path(metadata.get("factor_source", "")).resolve()
        == (SOURCE_ROOT / category).resolve()
        and metadata.get("factor_versions") == ["raw"]
    )

def run_scope(
    engine: Any,
    categories: list[str],
    result_root: Path,
    start: str,
    end: str,
    scope: str,
) -> list[dict[str, Any]]:
    context = engine.build_market_context(
        constituents_path=PROJECT_ROOT / "data" / "zz500" / "zz500_daily_constituent_stock.parquet",
        status_path=DEFAULT_TRADING_STATUS_PATH,
        execution_prices=engine.DEFAULT_EXECUTION_PRICES,
        benchmark_path=engine.DEFAULT_BENCHMARK,
        start=start,
        end=end,
    )

    results: list[dict[str, Any]] = []
    for category in categories:
        destination = result_root / category
        if destination.exists():
            if not reusable_output(engine, destination, category, start, end):
                raise FileExistsError(f"已有结果不可安全复用：{destination}")
            result: dict[str, Any] = {"factor": category, "status": "already_completed"}
        else:
            result = engine.run_factor(
                factor_name=category,
                factor_source_root=SOURCE_ROOT,
                output_root=result_root,
                context=context,
                initial_capital=INITIAL_CAPITAL,
                minimum_coverage=MINIMUM_COVERAGE,
                versions=("raw",),
            )
        print(json.dumps(portable_payload(result), ensure_ascii=False), flush=True)
        if result["status"] not in {"completed", "already_completed"}:
            raise RuntimeError(f"{category} 回测失败：{result}")

        metadata_path = destination / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["factor_version"] = MODEL
        metadata["factor_column"] = f"{category}_mlp"
        metadata["field_adapter"] = "MLP scalar scores from raw.parquet"
        metadata["report_scope"] = scope
        metadata["fees"]["slippage"] = 0.0
        metadata_path.write_text(
            json.dumps(portable_payload(metadata), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        results.append({"scope": scope, **result})
    return results

def curve_and_metrics(rows: pd.DataFrame, return_column: str) -> dict[str, Any]:
    if rows.empty:
        raise ValueError("区间内没有周收益记录")
    rows = rows.sort_values("week_last_trade")
    returns = rows[return_column].astype(float).to_numpy()
    nav = np.concatenate(([1.0], np.cumprod(1.0 + returns)))
    peaks = np.maximum.accumulate(nav)
    volatility = float(np.std(returns, ddof=1) * math.sqrt(52)) if len(returns) > 1 else 0.0
    sharpe = (
        float(np.mean(returns) / np.std(returns, ddof=1) * math.sqrt(52))
        if len(returns) > 1 and np.std(returns, ddof=1) > 0.0
        else 0.0
    )
    return {
        "dates": [str(rows.iloc[0]["week_first_trade"])]
        + rows["week_last_trade"].astype(str).tolist(),
        "curve": [finite(value) for value in nav],
        "total_return": finite(nav[-1] - 1.0),
        "maximum_drawdown": finite(np.min(nav / peaks - 1.0)),
        "annualized_weekly_volatility": finite(volatility),
        "weekly_sharpe_zero_rate": finite(sharpe),
        "positive_week_ratio": finite(np.mean(returns > 0.0)),
        "week_count": int(len(rows)),
        "effective_start": str(rows.iloc[0]["week_first_trade"]),
        "effective_end": str(rows.iloc[-1]["week_last_trade"]),
    }

def strategy_period(rows: pd.DataFrame) -> dict[str, Any]:
    metrics = curve_and_metrics(rows, "weekly_return")
    benchmark_total = float(np.prod(1.0 + rows["benchmark_return"].astype(float)) - 1.0)
    metrics.update(
        {
            "total_excess_return": finite(
                (1.0 + float(metrics["total_return"])) / (1.0 + benchmark_total) - 1.0
            ),
            "total_fees": rows.attrs["summary"][rows.direction.iloc[0]]["total_fees"],
            "mean_one_way_turnover": rows.attrs["summary"][rows.direction.iloc[0]]["mean_one_way_turnover"],
            "rebalanced_week_count": rows.attrs["summary"][rows.direction.iloc[0]]["rebalanced_week_count"],
        }
    )
    return metrics

def benchmark_period(rows: pd.DataFrame) -> dict[str, Any]:
    return curve_and_metrics(rows, "benchmark_return")

def build_html(report: list[dict[str, Any]]) -> str:
    data = json.dumps(portable_payload(report), ensure_ascii=False, separators=(",", ":"))
    template = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MLP V5增强版十类别因子收益回测</title>
<style>
:root{--bg:#08111f;--panel:#111d2e;--line:#2a3a51;--text:#e8eef8;--muted:#91a1b8;--high:#37d6a0;--low:#ffad5a;--bench:#7aa7ff;--accent:#b38cff}*{box-sizing:border-box}body{margin:0;background:linear-gradient(145deg,#07101c,#0d1727);color:var(--text);font-family:Inter,"Noto Sans SC",system-ui,sans-serif}.wrap{max-width:1320px;margin:auto;padding:24px}.head{display:flex;gap:18px;align-items:flex-end;justify-content:space-between;flex-wrap:wrap}.kicker{color:var(--bench);font-size:13px;letter-spacing:.12em}.title{font-size:28px;font-weight:750;margin:5px 0}.sub{color:var(--muted);font-size:13px;line-height:1.65}.controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap}button,select{background:#17253a;color:var(--text);border:1px solid #334966;border-radius:9px;padding:9px 12px;font-size:14px}button{cursor:pointer}button:hover,select:hover{border-color:var(--bench)}select{min-width:190px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:20px 0}.card,.chartbox,.tablebox,.notes{background:rgba(17,29,46,.92);border:1px solid var(--line);border-radius:14px;padding:16px}.card .label{color:var(--muted);font-size:12px}.card .value{font-size:25px;font-variant-numeric:tabular-nums;margin:6px 0}.card .detail{font-size:12px;color:var(--muted);line-height:1.7}.high{color:var(--high)}.low{color:var(--low)}.bench{color:var(--bench)}.chartbox{height:510px;position:relative}.legend{display:flex;gap:18px;font-size:13px;margin-bottom:8px;flex-wrap:wrap}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}canvas{width:100%;height:438px;display:block}.tooltip{position:absolute;display:none;pointer-events:none;background:#050a12ed;border:1px solid #405675;border-radius:8px;padding:9px;font-size:12px;white-space:nowrap;z-index:2}.tablebox{margin-top:12px;overflow-x:auto}.tabletitle{font-size:15px;font-weight:700;margin-bottom:10px}.hint{font-size:12px;color:var(--muted);font-weight:400;margin-left:8px}table{width:100%;border-collapse:collapse;font-size:13px;min-width:760px}th,td{padding:9px 10px;border-bottom:1px solid #26364c;text-align:right;font-variant-numeric:tabular-nums}th:first-child,td:first-child{text-align:left}thead{color:var(--muted)}tbody tr{cursor:pointer}tbody tr:hover,tbody tr.active{background:#182940}.notes{margin-top:12px;color:var(--muted);font-size:12px;line-height:1.75}@media(max-width:800px){.grid{grid-template-columns:1fr}.chartbox{height:420px}canvas{height:348px}.wrap{padding:14px}select{min-width:150px}.title{font-size:23px}}
</style></head><body><div class="wrap">
<div class="head"><div><div class="kicker">TEN CATEGORY MLP · WEEKLY NET RETURN</div><div class="title" id="title"></div><div class="sub" id="subtitle"></div></div><div class="controls"><button id="prev">← 上一个</button><select id="factor" aria-label="因子类别"></select><select id="period" aria-label="查看年份"></select><button id="next">下一个 →</button></div></div>
<div class="grid"><div class="card"><div class="label" id="highLabel"></div><div class="value high" id="highRet"></div><div class="detail" id="highDetail"></div></div><div class="card"><div class="label" id="lowLabel"></div><div class="value low" id="lowRet"></div><div class="detail" id="lowDetail"></div></div><div class="card"><div class="label" id="benchLabel"></div><div class="value bench" id="benchRet"></div><div class="detail" id="benchDetail"></div></div></div>
<div class="chartbox"><div class="legend"><span><i class="dot" style="background:var(--high)"></i>Higher 净值</span><span><i class="dot" style="background:var(--low)"></i>Lower 净值</span><span><i class="dot" style="background:var(--bench)"></i>中证500净值</span></div><canvas id="chart"></canvas><div class="tooltip" id="tooltip"></div></div>
<div class="tablebox"><div class="tabletitle">分年度收益率<span class="hint">点击年份切换上方曲线；超额收益按复利比值计算</span></div><table><thead><tr><th>年份</th><th>Higher</th><th>Higher超额</th><th>Lower</th><th>Lower超额</th><th>中证500</th><th>周数</th></tr></thead><tbody id="yearRows"></tbody></table></div>
<div class="notes">回测口径：仅使用完整自然周，周首交易日收盘调仓，周末交易日收盘估值；买入排名前20%，已有持仓处于前30%则继续持有，最终入选股票等权。策略收益已扣佣金、最低佣金、过户费及卖出印花税，滑点为0。基准为中证500指数（CSI 500，000905）。全时段曲线采用跨年连续持仓；每个单年度视图均为独立回测，初始资金重置为100万元，只纳入首尾交易日都位于该公历年的完整自然周，策略与基准净值均从1开始。</div>
</div><script>
const DATA=__DATA__;let factorIndex=0,periodKey='all';const factorSelect=document.getElementById('factor'),periodSelect=document.getElementById('period');
DATA.forEach((x,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`${x.label} · ${x.name}`;factorSelect.appendChild(o)});
const periodKeys=Object.keys(DATA[0].periods);periodKeys.forEach(k=>{const o=document.createElement('option');o.value=k;o.textContent=k==='all'?'全时段（2025–2026）':`${k}年${k==='2026'?'（截至6月）':''}`;periodSelect.appendChild(o)});
const pct=x=>x==null?'N/A':`${x>=0?'+':''}${(x*100).toFixed(2)}%`;const money=x=>x==null?'N/A':`¥${x.toLocaleString('zh-CN',{maximumFractionDigits:2})}`;const num=x=>x==null?'N/A':x.toFixed(2);
function strategyDetail(m){return `超额 ${pct(m.total_excess_return)}　最大回撤 ${pct(m.maximum_drawdown)}<br>年化波动 ${pct(m.annualized_weekly_volatility)}　周频夏普 ${num(m.weekly_sharpe_zero_rate)}<br>费用 ${money(m.total_fees)}　平均单边换手 ${pct(m.mean_one_way_turnover)}`}
function benchmarkDetail(m){return `最大回撤 ${pct(m.maximum_drawdown)}　年化波动 ${pct(m.annualized_weekly_volatility)}<br>周频夏普 ${num(m.weekly_sharpe_zero_rate)}　上涨周占比 ${pct(m.positive_week_ratio)}<br>${m.effective_start} 至 ${m.effective_end}，${m.week_count}周`}
function returnLabel(prefix,p){return `${p.label}${periodKey==='all'?'累计':'年度'}收益 · ${prefix}`}
function renderTable(d){const body=document.getElementById('yearRows');body.innerHTML='';periodKeys.filter(k=>k!=='all').forEach(k=>{const p=d.periods[k],tr=document.createElement('tr');if(k===periodKey)tr.className='active';tr.innerHTML=`<td>${k}${k==='2026'?' YTD':''}</td><td class="high">${pct(p.higher.total_return)}</td><td>${pct(p.higher.total_excess_return)}</td><td class="low">${pct(p.lower.total_return)}</td><td>${pct(p.lower.total_excess_return)}</td><td class="bench">${pct(p.benchmark.total_return)}</td><td>${p.higher.week_count}</td>`;tr.onclick=()=>{periodKey=k;periodSelect.value=k;render()};body.appendChild(tr)})}
function render(){const d=DATA[factorIndex],p=d.periods[periodKey],h=p.higher,l=p.lower,b=p.benchmark;factorSelect.value=factorIndex;periodSelect.value=periodKey;document.getElementById('title').innerHTML=`${d.label} MLP · ${p.label}收益曲线<div class="sub">字段：${d.factor_column}</div>`;document.getElementById('subtitle').textContent=`${p.label}完整自然周 · ${h.effective_start} 至 ${h.effective_end} · ${h.week_count}周 · 单年度净值起点重置为1`;document.getElementById('highLabel').textContent=returnLabel('因子值越大越优（higher）',p);document.getElementById('lowLabel').textContent=returnLabel('因子值越小越优（lower）',p);document.getElementById('benchLabel').textContent=returnLabel('中证500基准（benchmark）',p);document.getElementById('highRet').textContent=pct(h.total_return);document.getElementById('lowRet').textContent=pct(l.total_return);document.getElementById('benchRet').textContent=pct(b.total_return);document.getElementById('highDetail').innerHTML=strategyDetail(h);document.getElementById('lowDetail').innerHTML=strategyDetail(l);document.getElementById('benchDetail').innerHTML=benchmarkDetail(b);renderTable(d);draw(p)}
factorSelect.onchange=e=>{factorIndex=+e.target.value;render()};periodSelect.onchange=e=>{periodKey=e.target.value;render()};document.getElementById('prev').onclick=()=>{factorIndex=(factorIndex-1+DATA.length)%DATA.length;render()};document.getElementById('next').onclick=()=>{factorIndex=(factorIndex+1)%DATA.length;render()};
const canvas=document.getElementById('chart'),tip=document.getElementById('tooltip');let hit=[];
function draw(pdata){const rect=canvas.getBoundingClientRect(),ratio=Math.min(devicePixelRatio||1,2);canvas.width=rect.width*ratio;canvas.height=rect.height*ratio;const c=canvas.getContext('2d');c.setTransform(ratio,0,0,ratio,0,0);const W=rect.width,H=rect.height,p={l:64,r:22,t:18,b:42},dates=pdata.benchmark.dates,series=[{name:'Higher',v:pdata.higher.curve,color:'#37d6a0'},{name:'Lower',v:pdata.lower.curve,color:'#ffad5a'},{name:'中证500',v:pdata.benchmark.curve,color:'#7aa7ff'}],vals=series.flatMap(s=>s.v.filter(Number.isFinite));let lo=Math.min(...vals),hi=Math.max(...vals),pad=Math.max((hi-lo)*.12,.015);lo-=pad;hi+=pad;const x=i=>p.l+i*(W-p.l-p.r)/Math.max(dates.length-1,1),y=v=>p.t+(hi-v)*(H-p.t-p.b)/(hi-lo);c.clearRect(0,0,W,H);c.font='12px system-ui';c.textAlign='right';c.textBaseline='middle';for(let i=0;i<=5;i++){const v=lo+(hi-lo)*i/5,Y=y(v);c.strokeStyle='#26364c';c.lineWidth=1;c.beginPath();c.moveTo(p.l,Y);c.lineTo(W-p.r,Y);c.stroke();c.fillStyle='#91a1b8';c.fillText(v.toFixed(2),p.l-9,Y)}c.textAlign='center';[0,Math.floor((dates.length-1)/2),dates.length-1].forEach(i=>{c.fillStyle='#91a1b8';c.fillText(dates[i],x(i),H-17)});series.forEach(s=>{c.strokeStyle=s.color;c.lineWidth=2.2;c.beginPath();let started=false;s.v.forEach((v,i)=>{if(v==null)return;if(!started){c.moveTo(x(i),y(v));started=true}else c.lineTo(x(i),y(v))});c.stroke()});hit=dates.map((date,i)=>({x:x(i),date,values:series.map(s=>s.v[i])}))}
canvas.onmousemove=e=>{if(!hit.length)return;const r=canvas.getBoundingClientRect(),mx=e.clientX-r.left,q=hit.reduce((a,b)=>Math.abs(b.x-mx)<Math.abs(a.x-mx)?b:a),fmt=v=>v==null?'N/A':v.toFixed(4);tip.style.display='block';tip.style.left=`${Math.min(q.x+14,r.width-205)}px`;tip.style.top='48px';tip.innerHTML=`${q.date}<br><span class="high">Higher ${fmt(q.values[0])}</span><br><span class="low">Lower ${fmt(q.values[1])}</span><br><span class="bench">中证500 ${fmt(q.values[2])}</span>`};canvas.onmouseleave=()=>tip.style.display='none';window.onresize=()=>draw(DATA[factorIndex].periods[periodKey]);render();
</script></body></html>'''
    return template.replace("__DATA__", data)

ROOT = PROJECT_ROOT

MODEL = "v5_denoised_enhance_8y_ic10_return40_only_2025_2026"

SOURCE_ROOT = (
    ROOT / "outputs_mlp_v5_denoised_enhance_only_2025_2026" / "final"
)

RESULT_ROOT = ROOT / "mlp_v5_denoised_enhance_only_2025_2026_return_results"

START = "2025-01-01"

END = "2026-06-30"

DASHBOARD = (
    ROOT / "mlp_v5_denoised_enhance_only_2025_2026_annual_return_dashboard.html"
)

SUMMARY = ROOT / "mlp_v5_denoised_enhance_only_2025_2026_period_summary.parquet"

ANNUAL_SUMMARY = (
    ROOT / "mlp_v5_denoised_enhance_only_2025_2026_annual_summary.parquet"
)

SOURCES = ROOT / "mlp_v5_denoised_enhance_only_2025_2026_factor_sources.parquet"

MANIFEST = ROOT / "mlp_v5_denoised_enhance_only_2025_2026_return_manifest.json"

BATCH_RESULTS = (
    ROOT / "mlp_v5_denoised_enhance_only_2025_2026_batch_results.parquet"
)

YEARS = (2025, 2026)

def run_backtests(engine: Any, categories: list[str]) -> list[dict[str, Any]]:
    results = run_scope(
        engine, categories, RESULT_ROOT, START, END, "all"
    )
    for year in YEARS:
        results.extend(
            run_scope(
                engine,
                categories,
                RESULT_ROOT / "yearly" / str(year),
                f"{year}-01-01",
                f"{year}-12-31" if year < 2026 else END,
                str(year),
            )
        )
    return results

def build_report(
    categories: list[str],
) -> tuple[list[dict[str, Any]], pd.DataFrame, pd.DataFrame]:
    report: list[dict[str, Any]] = []
    full_summaries: list[pd.DataFrame] = []
    period_rows: list[dict[str, Any]] = []

    for category in categories:
        result_dir = RESULT_ROOT / category
        weekly, summary = load_return_report(result_dir)
        if set(weekly["direction"]) != {"higher", "lower"} or len(summary) != 2:
            raise ValueError(f"{category}缺少higher/lower结果")
        summary.insert(1, "category_cn", CATEGORY_LABELS[category])
        full_summaries.append(summary)

        higher_all = weekly.loc[weekly["direction"].eq("higher")].copy()
        lower_all = weekly.loc[weekly["direction"].eq("lower")].copy()
        periods: dict[str, dict[str, Any]] = {}
        for period_key in ["all", *[str(year) for year in YEARS]]:
            if period_key == "all":
                higher = higher_all
                lower = lower_all
                label = "全时段"
            else:
                year_weekly, _ = load_return_report(RESULT_ROOT / "yearly" / period_key / category)
                higher = year_weekly.loc[year_weekly["direction"].eq("higher")]
                lower = year_weekly.loc[year_weekly["direction"].eq("lower")]
                label = f"{period_key}年"

            high_metrics = strategy_period(higher)
            low_metrics = strategy_period(lower)
            benchmark_metrics = benchmark_period(higher)
            if (
                high_metrics["dates"] != low_metrics["dates"]
                or high_metrics["dates"] != benchmark_metrics["dates"]
            ):
                raise ValueError(f"{category}/{period_key}三条曲线日期不一致")
            periods[period_key] = {
                "label": label,
                "higher": high_metrics,
                "lower": low_metrics,
                "benchmark": benchmark_metrics,
            }
            for direction, metrics in (
                ("higher", high_metrics),
                ("lower", low_metrics),
            ):
                period_rows.append(
                    {
                        "factor_name": category,
                        "category_cn": CATEGORY_LABELS[category],
                        "period": period_key,
                        "period_label": label,
                        "direction": direction,
                        "effective_start": metrics["effective_start"],
                        "effective_end": metrics["effective_end"],
                        "week_count": metrics["week_count"],
                        "total_return": metrics["total_return"],
                        "benchmark_total_return": benchmark_metrics["total_return"],
                        "total_excess_return": metrics["total_excess_return"],
                        "maximum_drawdown": metrics["maximum_drawdown"],
                        "annualized_weekly_volatility": metrics[
                            "annualized_weekly_volatility"
                        ],
                        "weekly_sharpe_zero_rate": metrics[
                            "weekly_sharpe_zero_rate"
                        ],
                        "positive_week_ratio": metrics["positive_week_ratio"],
                        "total_fees": metrics["total_fees"],
                        "mean_one_way_turnover": metrics[
                            "mean_one_way_turnover"
                        ],
                    }
                )
        report.append(
            {
                "name": category,
                "label": CATEGORY_LABELS[category],
                "factor_column": f"{category}_mlp",
                "periods": periods,
            }
        )
    return (
        report,
        pd.concat(full_summaries, ignore_index=True),
        pd.DataFrame(period_rows),
    )

def main() -> None:
    categories, file_counts = validate_sources()
    engine = load_engine()
    results = run_backtests(engine, categories)
    write_output_parquet(pd.DataFrame(results), BATCH_RESULTS)

    for metadata_path in RESULT_ROOT.glob("**/metadata.json"):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["factor_version"] = MODEL
        metadata_path.write_text(
            json.dumps(portable_payload(metadata), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    report, summary, annual_summary = build_report(categories)
    write_output_parquet(summary, SUMMARY)
    write_output_parquet(annual_summary, ANNUAL_SUMMARY)
    write_output_parquet(pd.DataFrame(
        [
            {
                "factor_name": category,
                "category_cn": CATEGORY_LABELS[category],
                "factor_column": f"{category}_mlp",
                "source_symbol_count": file_counts[category],
            }
            for category in categories
        ]
    ), SOURCES)

    DASHBOARD.write_text(portable_payload(build_html(report)), encoding="utf-8")

    source_manifest_path = (
        ROOT
        / "outputs_mlp_v5_denoised_enhance_only_2025_2026"
        / "run_manifest.json"
    )
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    manifest = {
        "status": "completed",
        "model": MODEL,
        "factor_source_root": str(SOURCE_ROOT),
        "source_run_manifest": str(source_manifest_path),
        "source_training_contract": {
            "training_months": source_manifest["training_months"],
            "factor_selection": source_manifest["factor_selection"],
            "stock_selection": source_manifest["stock_selection"],
            "training": source_manifest["training"],
            "hidden_activation": source_manifest["hidden_activation"],
            "model_output": source_manifest["model_output"],
            "loss": source_manifest["loss"],
            "epochs": source_manifest["epochs"],
        },
        "factor_value_contract": (
            "sum(prob_group_k * k), k=1..5, higher_is_better"
        ),
        "categories": categories,
        "directions": ["higher", "lower"],
        "requested_start": START,
        "requested_end": END,
        "year_partition": "independent_calendar_year_requested_intervals",
        "year_curve_policy": (
            "independent_backtest_reset_initial_capital_and_nav_to_1"
        ),
        "return_engine": str(PROJECT_ROOT / "return_engine.py"),
        "benchmark": "CSI 500 / 000905",
        "initial_capital": INITIAL_CAPITAL,
        "minimum_coverage": MINIMUM_COVERAGE,
        "dashboard": str(DASHBOARD),
        "period_summary": str(SUMMARY),
        "annual_summary": str(ANNUAL_SUMMARY),
        "result_root": str(RESULT_ROOT),
        "dashboard_sha256": sha256(DASHBOARD),
        "period_summary_sha256": sha256(SUMMARY),
        "annual_summary_sha256": sha256(ANNUAL_SUMMARY),
        "sources_sha256": sha256(SOURCES),
    }
    MANIFEST.write_text(
        json.dumps(portable_payload(manifest), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"DONE categories={len(categories)} annual_rows={len(annual_summary)} "
        f"dashboard={DASHBOARD}",
        flush=True,
    )

if __name__ == "__main__":
    main()
