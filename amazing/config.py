from .exceptions import ConfigError
from dataclasses import dataclass

REQUIRED_KEYS = {
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
}

DEFAULT_SEED = 42
DEFAULT_ALGORITHM = "dfs"
ALGORITHMS = {"dfs", "prim", "kruskal"}

@dataclass(frozen=True)
class MazeConfig:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int
    algorithm: str

def read_config(file_name: str) -> dict[str, str]:
    config: dict[str, str] = dict()
    try:
        with open(file_name, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(f"Invaild config syntax: {line}")
                key, value = line.split("=", 1)
                if not key or not value:
                    raise ConfigError(f"Invalide config syntxt: {line}")
                if key in config:
                    raise ConfigError(f"Duplicate config key: {key}")
                config[key.strip()] = value.strip()
    except FileNotFoundError as error:
        raise ConfigError(f"Config file not found: {file_name}"
                          ) from error
    except PermissionError as error:
        raise ConfigError(f"Permission denied: {file_name}"
                           ) from error
    except OSError as error:
        raise ConfigError(f"Cannot read config file: {file_name}"
                          ) from error
    return config

def validate_required_key(data: dict[str, str]) -> None:
    for key in REQUIRED_KEYS:
        if key not in data:
            raise ConfigError(f"Missing required key: {key}")

def parse_coordinate(value: str) -> tuple[int, int]:
    parts: list[str] = value.split(",")

    if len(parts) != 2:
        raise ConfigError(
            f"Invalid coordinate: {value}. Expected format: x, y"
            )
    try:
        x = int(parts[0])
        y = int(parts[1])
    except ValueError as error:
        raise ConfigError(
            f"Invalid coordinate: {value}. "
            "Coordinates must be integers"
        ) from error

    return (x, y)

def parse_perfect(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False

    raise ConfigError("PERFECT must be True or False")

def parse_config(raw_data: dict[str, str]) -> MazeConfig:
    try:
        width = int(raw_data["WIDTH"])
        height = int(raw_data["HEIGHT"])
    except ValueError as error:
        raise ConfigError("WIDTH and HEIGHT must be integers") from error
    
    entry = parse_coordinate(raw_data["ENTRY"])
    exit = parse_coordinate(raw_data["EXIT"])

    output_file = raw_data["OUTPUT_FILE"]

    perfect = parse_perfect(raw_data["PERFECT"])

    if "SEED" in raw_data:
        try:
            seed = int(raw_data["SEED"])
        except ValueError as error:
            raise ConfigError("SEED must be an integer") from error
    else:
        seed = DEFAULT_SEED

    if "ALGORITHM" in raw_data:
        algorithm = raw_data["ALGORITHM"].lower()
        if algorithm not in ALGORITHMS:
            raise ConfigError(
                f"Invalid algorithm: {algorithm}. "
                f"Expected one of: {', '.join(sorted(ALGORITHMS))}"
            )
    else:
        algorithm = DEFAULT_ALGORITHM

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm
    )

def is_inside(position: tuple[int, int], width: int, height: int) -> bool:
    x = position[0]
    y = position[1]
    return (0 <= x < width and 0 <= y < height)

def validate_config(config: MazeConfig) -> None:
    if config.width <= 0:
        raise ConfigError("WIDTH must be greater than 0")
    if config.height <= 0:
        raise ConfigError("HEIGHT must be greater than 0")
    if not is_inside(config.entry, config.width, config.height):
            raise ConfigError("ENTRY is outside maze bounds")
    if not is_inside(config.exit, config.width, config.height):
            raise ConfigError("EXIT is outside maze bounds")
    if config.entry == config.exit:
        raise ConfigError("ENTRY and EXIT must be different")

def load_config(file_name: str) -> MazeConfig:
    data = read_config(file_name)

    validate_required_key(data)

    config: MazeConfig = parse_config(data)

    validate_config(config)

    return config