"""FinTA

公式：源码算子/递推链：df = ohlc.shift()；r4 = pp + (df['high'] - df['low']) * 1.382；r3 = pp + (df['high'] - df['low']) * 1；r2 = pp + (df['high'] - df['low']) * 0.618；r1 = pp + (df['high'] - df['low']) * 0.382；s1 = pp - (df['high'] - df['low']) * 0.382；s2 = pp - (df['high'] - df['low']) * 0.618；s3 = pp - (df['high'] - df['low']) * 1；s4 = pp - (df['high'] - df['low']) * 1.382；输出=concat([pp, Series(s1, name='s1'), Series(s2, name='s2'), Series(s3, name='s3'), Series(s4, name='s4'), Series(r1, name='r1'), Series(r2, name='r2'), Series(r3, name='r3'), Series(r4, name='r4')], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1162)。；固定默认参数={}；实际单列输出='r1'；；原目录：PIVOT_FIB（无固定窗口）；追踪：PF00999；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_pivot_fib_r1_2d', 'root_function': 'TA.PIVOT_FIB', 'parameters': {}, 'output_index': 5, 'output_label': 'r1', 'kernel': 'kernel_10b705905ba3cc5a', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_pivot_fib_r1_2d', {})
class Factor_finta_pivot_fib_r1_2d(PublicFactor):
    name = 'finta_pivot_fib_r1_2d'
    description = "源码算子/递推链：df = ohlc.shift()；r4 = pp + (df['high'] - df['low']) * 1.382；r3 = pp + (df['high'] - df['low']) * 1；r2 = pp + (df['high'] - df['low']) * 0.618；r1 = pp + (df['high'] - df['low']) * 0.382；s1 = pp - (df['high'] - df['low']) * 0.382；s2 = pp - (df['high'] - df['low']) * 0.618；s3 = pp - (df['high'] - df['low']) * 1；s4 = pp - (df['high'] - df['low']) * 1.382；输出=concat([pp, Series(s1, name='s1'), Series(s2, name='s2'), Series(s3, name='s3'), Series(s4, name='s4'), Series(r1, name='r1'), Series(r2, name='r2'), Series(r3, name='r3'), Series(r4, name='r4')], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1162)。；固定默认参数={}；实际单列输出='r1'；；原目录：PIVOT_FIB（无固定窗口）；追踪：PF00999；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
