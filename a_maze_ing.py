from amazing import load_config
from amazing import MazeRenderer
from mazegen import MazeGenerator
from mazegen import MazeConfig
from mazegen import MazeError
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("Invalid parse format")
        exit()
    try:
        config: MazeConfig = load_config(sys.argv[1])
        generator = MazeGenerator(config)
        generator.generate()
        generator.output_mazefile()
        renderer = MazeRenderer(generator, config)
        renderer.run()
    except MazeError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
