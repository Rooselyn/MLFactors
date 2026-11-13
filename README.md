# MLFactors

中证500横截面因子研究框架，支持因子计算、市值与行业中性化、每日信息系数（Information Coefficient, IC）、自然周账户回测、Markdown／HTML 报告，以及滚动筛选和多层感知机（Multilayer Perceptron, MLP）训练。

仓库包含源码、配置和研究文档，**不包含 `data/` 原始数据和 `outputs/` 计算结果**。运行前需自行准备数据。默认因子计算区间为 **2014-01-02 至 2026-06-30**，报告评估区间为 **2020-01-01 至 2026-06-30**；长窗口会额外读取可用历史，实际有效起点取决于输入覆盖和公式要求。

## 项目结构

```text
MLFactors/
├── config/                  # 日线、分钟、扩展及财报因子配置
├── factors/
│   ├── base.py              # 因子基础接口与通用数值实现
│   ├── inputs.py            # 输入声明、分区读取与时点对齐
│   ├── registry.py          # 因子注册、类别和共享 ID 校验
│   ├── _numeric_native.c    # 原生数值内核源码
│   └── 各类别目录/           # 独立因子实现
├── mlp/                     # MLP 训练与回测展示
├── tmp/                     # 数据字段、因子公式及研究记录
├── dataloader.py            # Parquet 读写、成分股与状态处理
├── neutralization.py        # 市值与行业中性化
├── factors_eval.py          # IC、衰减与显著性检验
├── return_engine.py         # 持股账户、交易费用与自然周收益
├── factor_report.py         # Markdown 与交互式 HTML 报告
├── factors_select.py        # 滚动筛选、因子拼接与评估
└── run.py                   # 单因子与全量流程入口
```

运行时在项目内建立 `data/zz500/` 和 `outputs/zz500/`。两者均由 `.gitignore` 整目录排除；Python 字节码缓存、运行日志及 `.runtime/` 也不入库。

## 环境

使用 Python 3.10 环境。核心依赖包括 `numpy`、`pandas`、`pyarrow`、`scipy`、`statsmodels`、`scikit-learn`、`torch` 和 `tqdm`；MLP 正式训练需要可用的 CUDA GPU。并行因子流程使用 Linux 的 `fork` 进程方式。

以下命令均在项目根目录执行，并使用已安装依赖的 Python：

```bash
cd /path/to/MLFactors
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

python -B -c 'import numpy, pandas, pyarrow, scipy, statsmodels, sklearn, torch, tqdm; print("依赖导入通过")'
python -B run.py --help
```

部分技术指标通过项目内 `_numeric_native.so` 运行，不依赖外部 TA-Lib／Tulip 安装。更换平台或需要重建时执行：

```bash
gcc -std=c99 -O2 -shared -fPIC factors/_numeric_native.c -lm -o factors/_numeric_native.so
```

## 配置与新增因子

| 配置 | 数量 | 用途 |
|---|---:|---|
| [`factor_configs_day_base.json`](config/factor_configs_day_base.json) | 4,920 | 日线基础因子，包含财报因子 |
| [`factor_configs_minute_base.json`](config/factor_configs_minute_base.json) | 547 | 分钟输入因子，输出日频信号 |
| [`factor_configs_day_expansion.json`](config/factor_configs_day_expansion.json) | 3,930 | 基础因子的变换与组合 |
| [`financial_factors.json`](config/financial_factors.json) | 174 | 财报时点处理名单，全部属于日线基础配置 |

日线基础与扩展合计 **8,850** 项，加上分钟因子共 **9,397** 项。扩展配置引用基础因子，不另建逐个扩展实现文件。

新增基础因子时，在 `factors/<类别>/` 建立独立 Python 文件，继承 `BaseFactor` 或 `MinuteFactor`，声明 `INPUTS`／`MINUTE_INPUTS`、公式和窗口，通过 `@register_factor` 注册，并加入对应基础 JSON。配置需包含模块路径、类名、参数、`category`、经济解释 `description`、`ID`，以及完整的公式定义；分钟配置用 `economic_category` 保存其经济类别。来源或批次专属的业务计算逻辑放在具体因子文件中。

基础名称使用小写字母、数字和下划线，末尾标明窗口；剔除近期的窗口可使用 `N`（net，剔除），例如 `252N10d`。文件名、配置键、类内 `name` 和输出目录保持一致。类别直接读取配置；分钟类别单独配置，财报因子属于日线。

**所有正式因子共用一个 ID 空间**，格式为 `R` 加五位数字：

- 日线和分钟基础因子从小向大分配，取两份基础配置最大 ID 加一。
- 扩展因子从大向小分配，取全部扩展配置最小 ID 减一。
- 保留既有 ID，不因更名或删除而重排；各配置按自身方向排序，跨配置名称和 ID 均须唯一，基础与扩展编号区间不得相交。
- 当前下一个基础 ID 为 `R05478`，下一个扩展 ID 为 `R96069`；新增前重新检查实际配置。

校验共享编号和扩展输入依赖：

```bash
python -B -c 'from factors.registry import validate_shared_factor_ids, load_factor_configs; print("共享因子数:", len(validate_shared_factor_ids())); load_factor_configs()'
```

## 数据接口

字段说明见 [`tmp/数据字段汇总.md`](tmp/数据字段汇总.md)。公式按各因子的输入声明投影读取，公共行情、成分股、交易状态和基准由 `run.py` 配置。原始输入限定在项目内 `data/zz500/`。

| 路径 | 内容 |
|---|---|
| `stock_day/YYYY/MM.parquet` | 日线行情、后复权价格、市值、换手率和行业 |
| `stock_minute/YYYY/MM.parquet` | 分钟 OHLC、成交量和成交额 |
| `financial_*/YYYY/MM.parquet` | 财务报表、财务指标和公告记录 |
| `broker_earnings_forecast/YYYY/MM.parquet` | 券商预测及研报日期 |
| `zz500_daily_constituent_stock.parquet` | `date, tickers`，每日成分股名单 |
| `zz500_daily_trading_status/YYYY/MM.parquet` | `trade_date, ts_code, is_st, is_suspended` |
| `zz500_daily_index/YYYY/MM.parquet` | 指数 `000905.SH` 的日行情与交易日历 |

表内股票连接键通常为 `trade_date, ts_code`，分钟时间列为 `trade_time`；具体日期列和科目以输入声明为准。分钟时间按 `Asia/Shanghai` 处理。日频成交量单位为手、成交额为千元、市值为万元；分钟成交量为股、成交额为元。日线后复权 VWAP 为 `amount * 10 / vol * adj_factor`，分钟价格按声明关联当日复权因子。

财报遵守时点可用性（Point-in-Time, PIT）：实际公告日优先使用 `f_ann_date`，缺失时使用 `ann_date`，不能把报告期末当成可用日。季度、年度滞后按报告期匹配，禁止利用未来修订；不确定的冲突按读取器规则留缺失或报错。价格窗口沿交易日滚动，不按自然周或自然月重置。

信号和交易按每日成分股、ST 及全天停牌状态筛选；状态缺失沿用代码中的 False 处理。中性化逐日回归对数市值及申万一级行业，取普通最小二乘法（Ordinary Least Squares, OLS）残差。公共回填采用先前向填充、再补 0，非当日成分股保持空值；不按退出后重新入池的区间拆分填充。

## 运行

### 单因子与基础批量流程

`single` 模式让每个因子独立完成 **因子值 → 每日 IC → 自然周收益 → Markdown／HTML 报告**。先查看计划，再去掉 `--plan-only` 执行：

```bash
python -B -u run.py --mode single \
  --factor-config config/factor_configs_day_base.json \
  --factor alpha158_beta_252n10d \
  --start 2014-01-02 --end 2026-06-30 --workers 1 --plan-only
```

去掉 `--factor` 可运行该配置中的全部基础因子，`--factor-prefix` 可按名称前缀筛选。分钟因子使用同一模式，改用分钟配置即可：

```bash
python -B -u run.py --mode single \
  --factor-config config/factor_configs_minute_base.json \
  --start 2014-01-02 --end 2026-06-30 --workers 80
```

并行数由 `--workers` 控制，应按内存及单因子耗时调整。多进程 `single` 模式记录普通因子任务异常并继续其余任务，全部任务结束后汇总失败并返回非零状态；成功项的结果保留。该模式重新计算所选因子，不自动跳过已有结果。

### 日线基础与扩展全流程

```bash
python -B -u run.py --pipeline \
  --factor-config config/factor_configs_day_base.json \
  --expansion-factor-config config/factor_configs_day_expansion.json \
  --start 2014-01-02 --end 2026-06-30 --workers 80
```

全流程先计算基础值及回填，再计算扩展值及回填，最后统一执行 IC、收益和报告阶段。各阶段完成后才进入下一阶段；阶段失败会阻止后续阶段。

若基础原始值和中性化值已齐备，仅计算扩展可增加 `--expansion-only`；该模式校验并复用基础值，缺失时报错，不触发基础重算。`--expansion-start <编号>` 可进一步限定扩展起点。扩展原始值从基础原始值计算，中性化值从基础中性化值计算后再中性化。

### 滚动筛选与 MLP

筛选和训练读取已完成的因子值、每日 IC 及自然周收益。先检查计划：

```bash
python -B factors_select.py --selection-mode ic --window 3y --plan-only
python -B factors_select.py --selection-mode return --window 3y --plan-only
python -B mlp/train_mlp.py --plan-only
```

去掉 `--plan-only` 执行。筛选月份使用 `--first-month`、`--final-month` 指定；训练参数见 `python -B mlp/train_mlp.py --help`。训练完成后运行 `python -B mlp/run_mlp_dashboard.py` 生成回测展示。表格产物统一使用 Parquet。

## 输出和评估口径

```text
outputs/zz500/
├── factor_value/<因子名>/{raw,neutralization}.parquet
├── factor_ic/<因子名>/{raw,neutralization}.parquet
├── factor_return/<因子名>/
│   ├── {raw,neutralization}.parquet
│   ├── report_portfolios.parquet
│   ├── report_return_metadata.json
│   └── metadata.json
└── factor_report/<因子名>/factor_report.{md,html}
```

- 因子值宽表包含 `signal_date, available_date` 和股票列；每日 IC 表包含相应日期列及 `IC_raw`／`IC_neutralization`。窗口预热、财报历史或分钟数据不足时可能没有有效值，文件存在不等于覆盖合格。
- IC 使用 5 日前向价格收益 `close[t+6] / close[t+1] - 1`；显著性采用 Newey–West 稳健标准误。标签依赖未来价格，实际有效截止可能早于请求截止。
- 组合收益由持股账户计算，使用未复权执行价格、100 股整手、现金与交易状态约束。默认佣金 0.03%（最低 5 元）、卖出印花税 0.10%、过户费 0.001%、滑点 0，均为代码固定回测参数。
- 原始与中性化版本分别按自身全时段未舍入 IC 均值确定方向：正值选 Top20%，负值选 Bottom20%，零或缺失不指定方向。年度或子区间比较沿用全时段方向，收益按完整自然周净收益复利累计。
- 五分组由低到高排列，Group1 为 Bottom20%，Group5 为 Top20%。单调性为 `abs(Kendall tau) * abs(Spearman rho)`；回撤基于包含期初净值 1 的周末净值路径。
- HTML 内嵌原始和中性化收益曲线、基准、年度切换及表格，离线可打开。回测元数据用于口径检查和结果复用，应与相应收益文件一起保留。

## 研究文档

- [数据字段汇总](tmp/数据字段汇总.md)
- [网络公开因子库：已实现](tmp/网络公开因子库-已实现.md)
- [网络公开因子：已实现](tmp/网络公开因子-已实现.md)
- [知乎公开因子：已实现](tmp/知乎公开因子-已实现.md)
- [自研因子：已实现](tmp/自研因子-已实现.md)
- [扩展因子淘汰记录](tmp/扩展因子淘汰记录.md)

各因子的来源、公式补全及本地修订以对应文档、配置和源码为准。报告中的历史收益来自指定数据与回测参数，不代表当前可交易收益。
