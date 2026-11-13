"""FinTA

公式：源码算子/递推链：df = ohlc.shift()；s1 = pivot * 2 - df['high']；s2 = pivot - (df['high'] - df['low'])；s3 = df['low'] - 2 * (df['high'] - pivot)；s4 = df['low'] - 3 * (df['high'] - pivot)；r1 = pivot * 2 - df['low']；r2 = pivot + (df['high'] - df['low'])；r3 = df['high'] + 2 * (pivot - df['low'])；r4 = df['high'] + 3 * (pivot - df['low'])；输出=concat([pivot, Series(s1, name='s1'), Series(s2, name='s2'), Series(s3, name='s3'), Series(s4, name='s4'), Series(r1, name='r1'), Series(r2, name='r2'), Series(r3, name='r3'), Series(r4, name='r4')], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1123)。；固定默认参数={}；实际单列输出='r3'；；原目录：PIVOT（无固定窗口）；追踪：PF00998；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_pivot_r3_2d', 'root_function': 'TA.PIVOT', 'parameters': {}, 'output_index': 7, 'output_label': 'r3', 'kernel': 'kernel_40f8466ae273e757', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_pivot_r3_2d', {})
class Factor_finta_pivot_r3_2d(PublicFactor):
    name = 'finta_pivot_r3_2d'
    description = "源码算子/递推链：df = ohlc.shift()；s1 = pivot * 2 - df['high']；s2 = pivot - (df['high'] - df['low'])；s3 = df['low'] - 2 * (df['high'] - pivot)；s4 = df['low'] - 3 * (df['high'] - pivot)；r1 = pivot * 2 - df['low']；r2 = pivot + (df['high'] - df['low'])；r3 = df['high'] + 2 * (pivot - df['low'])；r4 = df['high'] + 3 * (pivot - df['low'])；输出=concat([pivot, Series(s1, name='s1'), Series(s2, name='s2'), Series(s3, name='s3'), Series(s4, name='s4'), Series(r1, name='r1'), Series(r2, name='r2'), Series(r3, name='r3'), Series(r4, name='r4')], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1123)。；固定默认参数={}；实际单列输出='r3'；；原目录：PIVOT（无固定窗口）；追踪：PF00998；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
