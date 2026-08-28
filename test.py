from amazing import load_config, MazeConfig
from amazing import ConfigError
from mazegen import MazeGenerator
import sys

def print_configs(config: MazeConfig) -> None:
    print(config.width)
    print(config.height)
    print(config.entry)
    print(config.exit)
    print(config.output_file)
    print(config.perfect)
    print(config.seed)

def main() -> None:
    if len(sys.argv) != 2:
        raise ConfigError(f"Invalid parse format")
    config: MazeConfig = load_config(sys.argv[1])
    print_configs(config)
    generator = MazeGenerator(config)
    generator.generate()
    generator.output_mazefile()

if __name__ == "__main__":
    main()