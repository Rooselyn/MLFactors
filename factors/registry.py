"""因子注册、配置发现与类别校验。"""

from __future__ import annotations

import json
import re
from pathlib import Path

from factors.base import BaseFactor, MinuteFactor


CATEGORY_NAMES = {
    "动量": "momentum",
    "反转": "reversal",
    "质量": "quality",
    "成长": "growth",
    "量价": "volume_price",
    "流动性": "liquidity",
    "风险": "risk",
    "规模": "size",
    "价值": "value",
    "无含义": "meaningless",
}
MINUTE_CATEGORY = "分钟"
CONFIG_DIRECTORY = Path(__file__).resolve().parents[1] / "config"
DEFAULT_BASE_FACTOR_CONFIG = CONFIG_DIRECTORY / "factor_configs_day_base.json"
DEFAULT_EXPANSION_FACTOR_CONFIG = CONFIG_DIRECTORY / "factor_configs_day_expansion.json"


FACTOR_NAME_PATTERN = re.compile(
    r"[a-z][a-z0-9_]*_(?:[1-9][0-9]*(?:[nN][1-9][0-9]*)?(?:d|min|m|q|y)|alld)"
)


def validate_factor_names(configs: dict) -> None:
    """只校验基础日频因子的规范名称；派生与分钟因子保持原身份。"""
    invalid = []
    for name, config in configs.items():
        if not isinstance(name, str) or not name:
            invalid.append(name)
            continue
        config = config or {}
        if (config.get("params", {}).get("expansion_kind")
                or config.get("module", "").startswith("factors.minute.")):
            continue
        if FACTOR_NAME_PATTERN.fullmatch(name) is None:
            invalid.append(name)
    if invalid:
        raise ValueError(f"因子名称不符合小写/字符/窗口规范: {invalid[:10]}")


def validate_factor_ids(configs: dict) -> None:
    """校验日线、分钟及扩展因子的 ID 格式与唯一性。"""
    validate_factor_names(configs)
    seen: dict[str, str] = {}
    for name, config in configs.items():
        factor_id = config.get("ID")
        if not isinstance(factor_id, str) or re.fullmatch(r"R[0-9]{5}", factor_id) is None:
            raise ValueError(f"{name} 的 ID 必须为 R 加五位数字字符串（例如 R00001）")
        if factor_id in seen:
            raise ValueError(f"因子 ID 重复: {factor_id} ({seen[factor_id]}, {name})")
        seen[factor_id] = name


def validate_shared_factor_ids(directory: Path = CONFIG_DIRECTORY) -> dict:
    """跨配置校验共享ID；基础递增、扩展递减，两个编号区间不得相交。"""
    configs = {}
    base_ids, expansion_ids = [], []
    filenames = (
        "factor_configs_day_base.json", "factor_configs_minute_base.json",
        "factor_configs_day_expansion.json", "factor_configs_minute_expansion.json",
    )
    for filename in filenames:
        path = directory / filename
        if filename == "factor_configs_minute_expansion.json" and not path.exists():
            continue
        part = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(part, dict):
            raise ValueError(f"{filename} 必须为因子配置字典")
        overlap = configs.keys() & part.keys()
        if overlap:
            raise ValueError(f"跨配置因子重名: {sorted(overlap)[:10]}")
        validate_factor_ids(part)
        numbers = [int(config["ID"][1:]) for config in part.values()]
        descending = filename.endswith("_expansion.json")
        if any(number == 0 for number in numbers):
            raise ValueError(f"{filename} 的ID必须在R00001至R99999之间")
        if numbers != sorted(numbers, reverse=descending):
            direction = "递减" if descending else "递增"
            raise ValueError(f"{filename} 的ID必须按配置顺序{direction}")
        (expansion_ids if descending else base_ids).extend(numbers)
        configs.update(part)
    validate_factor_ids(configs)
    if base_ids and expansion_ids and max(base_ids) >= min(expansion_ids):
        raise ValueError("基础与扩展因子的ID编号区间相交")
    return configs


def load_factor_configs(
    base_path: Path = DEFAULT_BASE_FACTOR_CONFIG,
    expansion_path: Path = DEFAULT_EXPANSION_FACTOR_CONFIG,
) -> dict:
    """分别读取纯基础与纯扩展配置，在内存中合并并校验身份及输入依赖。"""
    if (base_path.resolve() == DEFAULT_BASE_FACTOR_CONFIG.resolve()
            and expansion_path.resolve() == DEFAULT_EXPANSION_FACTOR_CONFIG.resolve()):
        validate_shared_factor_ids()
    base = json.loads(base_path.read_text(encoding="utf-8"))
    expansions = json.loads(expansion_path.read_text(encoding="utf-8"))
    if not isinstance(base, dict) or not base or not isinstance(expansions, dict):
        raise ValueError("基础配置必须为非空字典，扩展配置必须为字典")
    for name, config in base.items():
        if config.get("params", {}).get("expansion_kind"):
            raise ValueError(f"基础配置不能包含扩展因子: {name}")
    for name, config in expansions.items():
        if re.fullmatch(r"expansion_[0-9]{5}", name) is None:
            raise ValueError(f"扩展因子名称必须为 expansion_ 加五位数字: {name}")
        params = config.get("params", {})
        if params.get("expansion_kind") not in {"single_transform", "factor_combination"}:
            raise ValueError(f"扩展配置不能包含基础因子或未知扩展类型: {name}")
        if not set(params.get("input_factors", [])).issubset(base):
            raise ValueError(f"{name} 引用了基础配置中不存在的输入")
    overlap = base.keys() & expansions.keys()
    if overlap:
        raise ValueError(f"基础和扩展因子重名: {sorted(overlap)}")
    configs = {**base, **expansions}
    validate_factor_ids(configs)
    return configs


def load_categories(
    configs: dict | None = None,
    factor_names: set[str] | None = None,
) -> tuple[list[str], dict[str, str]]:
    """严格校验内嵌类别及因子覆盖范围，返回固定顺序的类别和逐因子映射。"""
    payload = load_factor_configs() if configs is None else configs
    if not isinstance(payload, dict) or not payload:
        raise ValueError("因子配置必须是非空字典")
    validate_factor_names(payload)
    allowed = {*CATEGORY_NAMES, MINUTE_CATEGORY}
    mapping: dict[str, str] = {}
    for name, config in payload.items():
        category = config.get("category") if isinstance(config, dict) else None
        if not isinstance(category, str) or category not in allowed:
            raise ValueError(f"因子 {name} 缺少有效category: {category!r}")
        mapping[name] = category
    if factor_names is not None:
        missing = factor_names - mapping.keys()
        extra = mapping.keys() - factor_names
        if missing or extra:
            raise ValueError(
                "类别配置与正式因子不一致: "
                f"missing={sorted(missing)[:10]}, extra={sorted(extra)[:10]}"
            )
    if "momentum_ml_252n20d" in mapping and mapping["momentum_ml_252n20d"] != "动量":
        raise ValueError("momentum_ml_252n20d必须固定属于动量类别")
    present = set(mapping.values())
    return [name for name in (*CATEGORY_NAMES, MINUTE_CATEGORY) if name in present], mapping


class FactorRegistry:
    """注册、获取和列出因子类。"""

    _registry: dict[str, type[BaseFactor]] = {}

    @classmethod
    def register(cls, factor_class: type[BaseFactor]) -> type[BaseFactor]:
        if not issubclass(factor_class, BaseFactor):
            raise TypeError("注册对象必须是 BaseFactor 子类")
        if not factor_class.name:
            raise ValueError(f"{factor_class.__name__} 必须定义非空的 name 属性")
        if not issubclass(factor_class, MinuteFactor):
            validate_factor_names({factor_class.name: None})
        class_name = factor_class.__name__
        if class_name in cls._registry:
            raise ValueError(f"因子类重复注册: {class_name}")
        cls._registry[class_name] = factor_class
        return factor_class

    @classmethod
    def get(cls, name: str) -> type[BaseFactor]:
        if name not in cls._registry:
            import importlib
            for config in cls._factor_configs().values():
                if config["relay_class"] == name:
                    importlib.import_module(config["module"])
                    break
        return cls._registry[name]

    @classmethod
    def list(cls) -> list[str]:
        return sorted(set(cls._registry) | {
            config["relay_class"] for config in cls._factor_configs().values()
        })

    @staticmethod
    def _factor_configs() -> dict:
        validate_shared_factor_ids()
        directory = Path(__file__).resolve().parents[1] / "config"
        configs = {}
        for filename in ("factor_configs_day_base.json", "factor_configs_minute_base.json"):
            part = json.loads((directory / filename).read_text(encoding="utf-8"))
            validate_factor_ids(part)
            overlap = configs.keys() & part.keys()
            if overlap:
                raise ValueError(f"基础和分钟因子重名: {sorted(overlap)}")
            configs.update(part)
        return configs


def register_factor(factor_class: type[BaseFactor]) -> type[BaseFactor]:
    """将 BaseFactor 子类注册到全局注册表。"""
    return FactorRegistry.register(factor_class)
