from amazing import load_config, MazeConfig
from amazing import MazeError
from amazing import MazeRenderer
from mazegen import MazeGenerator
import sys

# def print_choices() -> int:
#     print("=== A-Maze-ing ===")
#     print("1. Re-generate a new maze")
#     print("2. Show/Hide a valid shortest path")
#     print("3. Change maze wall colours")
#     print("4. Quit")
#     while True:
#         try:
#             choice: int = int(input("Choice?(1-4):"))
#             if choice < 1 or choice > 4:
#                 raise ValueError("Please enter an integer between 1 and 4")
#             break
#         except ValueError as error:
#             print(f"Error: {error}")
#     return choice

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

    # ##可視化するコードここに
    # print_choices
    # while True:
    #     choice: int = print_choices()
    #     match choice:
    #         case 1:
    #             generator.generate()
    #             generator.output_mazefile()
    #             ##可視化するやつ
    #         case 2:
    #             ##show/hide the shortest path
    #         case 3:
    #             ##rotate the wall colours
    #         case 4:
    #             exit()
    #         case _:
    #             print("Unknown choice")