"""MiniLibX renderer for generated mazes."""

from mlx import Mlx

from mazegen import MazeConfig
from mazegen import Cell, MazeGenerator
from mazegen import bfs
from mazegen import constants

Color = tuple[int, int, int, int]
Position = tuple[int, int]


class MazeRenderer:
    """Display and interact with a generated maze using MiniLibX."""

    CELL_SIZE = 24
    WALL_THICKNESS = 3
    MARGIN = 20
    CONTROL_HEIGHT = 45

    BACKGROUND_COLOR: Color = (20, 25, 35, 255)
    PATH_COLOR: Color = (245, 196, 66, 255)
    ENTRY_COLOR: Color = (55, 200, 110, 255)
    EXIT_COLOR: Color = (230, 75, 75, 255)
    PATTERN_COLOR: Color = (85, 100, 130, 255)
    TEXT_COLOR = 0xFFFFFFFF

    WALL_COLORS: tuple[Color, ...] = (
        (235, 240, 245, 255),
        (70, 205, 255, 255),
        (255, 100, 190, 255),
        (255, 180, 60, 255),
        (140, 235, 120, 255),
    )

    def __init__(
        self,
        generator: MazeGenerator,
        config: MazeConfig,
    ) -> None:
        """Create the MLX window and its matching image buffer."""
        self.generator = generator
        self.config = config
        self.rows = len(generator.grid)
        self.cols = len(generator.grid[0]) if generator.grid else 0
        if self.rows == 0 or self.cols == 0:
            raise RuntimeError("Cannot render an empty maze")

        maze_width = (
            self.cols * self.CELL_SIZE
            + self.MARGIN * 2
        )

        self.window_width = max(
            maze_width,
            600,
        )

        self.offset_x = (
            self.window_width - maze_width
        ) // 2

        self.window_height = (
            self.MARGIN * 2
            + self.rows * self.CELL_SIZE
            + self.WALL_THICKNESS
            + self.CONTROL_HEIGHT
        )

        self.show_path = False
        self.wall_color_index = 0
        self.path_cells: set[Position] = set()
        self._image_displayed = False
        self._cleaned_up = False

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            raise RuntimeError("Failed to initialize MLX")

        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr,
            self.window_width,
            self.window_height,
            "A-Maze-ing",
        )
        if not self.win_ptr:
            self.mlx.mlx_release(self.mlx_ptr)
            raise RuntimeError("Failed to create MLX window")

        self.img_ptr = self.mlx.mlx_new_image(
            self.mlx_ptr,
            self.window_width,
            self.window_height,
        )
        if not self.img_ptr:
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
            self.mlx.mlx_release(self.mlx_ptr)
            raise RuntimeError("Failed to create MLX image")

        (
            self.image_data,
            self.bits_per_pixel,
            self.size_line,
            self.image_format,
        ) = self.mlx.mlx_get_data_addr(self.img_ptr)

        if self.bits_per_pixel != 32:
            self.cleanup()
            raise RuntimeError(
                f"Unsupported bits per pixel: {self.bits_per_pixel}"
            )
        if self.image_format not in (0, 1):
            self.cleanup()
            raise RuntimeError(
                f"Unsupported image format: {self.image_format}"
            )

        self._refresh_path()

    @property
    def wall_color(self) -> Color:
        """Return the currently selected wall color."""
        return self.WALL_COLORS[self.wall_color_index]

    def _encode_color(self, color: Color) -> bytes:
        """Convert an RGBA tuple to the byte order required by MLX."""
        red, green, blue, alpha = color
        if self.image_format == 0:
            return bytes((blue, green, red, alpha))
        return bytes((alpha, red, green, blue))

    def put_pixel(self, x: int, y: int, color: Color) -> None:
        """Write one pixel into the image buffer, clipping outside points."""
        if not (
            0 <= x < self.window_width
            and 0 <= y < self.window_height
        ):
            return
        offset = y * self.size_line + x * 4
        self.image_data[offset:offset + 4] = self._encode_color(color)

    def fill_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Color,
    ) -> None:
        """Draw a clipped, filled rectangle into the image buffer."""
        left = max(x, 0)
        top = max(y, 0)
        right = min(x + width, self.window_width)
        bottom = min(y + height, self.window_height)
        if left >= right or top >= bottom:
            return

        pixel_row = self._encode_color(color) * (right - left)
        for current_y in range(top, bottom):
            offset = current_y * self.size_line + left * 4
            self.image_data[offset:offset + len(pixel_row)] = pixel_row

    def clear_image(self) -> None:
        """Fill the complete image with the background color."""
        self.fill_rect(
            0,
            0,
            self.window_width,
            self.window_height,
            self.BACKGROUND_COLOR,
        )

    def _cell_origin(self, x: int, y: int) -> Position:
        """Convert maze coordinates to the top-left window coordinate."""
        return (
            self.offset_x
            + self.MARGIN
            + x * self.CELL_SIZE,
            self.MARGIN
            + y * self.CELL_SIZE,
        )

    def fill_cell(self, x: int, y: int, color: Color) -> None:
        """Fill the inside of one maze cell without covering its walls."""
        screen_x, screen_y = self._cell_origin(x, y)
        padding = self.WALL_THICKNESS + 2
        inner_size = self.CELL_SIZE - padding * 2
        self.fill_rect(
            screen_x + padding,
            screen_y + padding,
            inner_size,
            inner_size,
            color,
        )

    def draw_cell_walls(self, cell: Cell) -> None:
        """Draw every closed wall of one cell."""
        x0, y0 = self._cell_origin(cell.x, cell.y)
        x1 = x0 + self.CELL_SIZE
        y1 = y0 + self.CELL_SIZE
        length = self.CELL_SIZE + self.WALL_THICKNESS

        if cell.has_wall(constants.NORTH):
            self.fill_rect(
                x0, y0, length, self.WALL_THICKNESS, self.wall_color
            )
        if cell.has_wall(constants.EAST):
            self.fill_rect(
                x1, y0, self.WALL_THICKNESS, length, self.wall_color
            )
        if cell.has_wall(constants.SOUTH):
            self.fill_rect(
                x0, y1, length, self.WALL_THICKNESS, self.wall_color
            )
        if cell.has_wall(constants.WEST):
            self.fill_rect(
                x0, y0, self.WALL_THICKNESS, length, self.wall_color
            )

    def _refresh_path(self) -> None:
        """Cache the current shortest path for quick redraws."""
        self.path_cells = set(
            bfs(
                self.generator.grid,
                self.generator._entry,
                self.generator._exit,
            )
        )

    def draw_maze(self) -> None:
        """Draw cell fills first and walls last so walls remain visible."""
        if self.show_path:
            for x, y in self.path_cells:
                self.fill_cell(x, y, self.PATH_COLOR)

        for row in self.generator.grid:
            for cell in row:
                if cell.blocked:
                    self.fill_cell(cell.x, cell.y, self.PATTERN_COLOR)

        entry_x, entry_y = self.config.entry
        exit_x, exit_y = self.config.exit
        self.fill_cell(entry_x, entry_y, self.ENTRY_COLOR)
        self.fill_cell(exit_x, exit_y, self.EXIT_COLOR)

        for row in self.generator.grid:
            for cell in row:
                self.draw_cell_walls(cell)

    def redraw(self) -> None:
        """Rebuild the image and display it in the window."""
        if self._image_displayed:
            self.mlx.mlx_sync(
                self.mlx_ptr,
                Mlx.SYNC_IMAGE_WRITABLE,
                self.img_ptr,
            )

        self.clear_image()
        self.draw_maze()
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_ptr,
            self.img_ptr,
            0,
            0,
        )
        self._image_displayed = True

        path_state = "ON" if self.show_path else "OFF"
        controls = (
            f"1: regenerate  2: path {path_state}  "
            "3: color  4/Q/ESC: quit"
        )
        text_y = self.window_height - self.CONTROL_HEIGHT + 14
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.MARGIN,
            text_y,
            self.TEXT_COLOR,
            controls,
        )

    def regenerate(self) -> None:
        """Generate a new maze, update its output and redraw it."""
        self.generator.generate()
        self.generator.output_mazefile()
        self._refresh_path()
        self.redraw()

    def toggle_path(self) -> None:
        """Toggle shortest-path visibility and redraw."""
        self.show_path = not self.show_path
        self.redraw()

    def rotate_wall_color(self) -> None:
        """Select the next wall color and redraw."""
        self.wall_color_index = (
            self.wall_color_index + 1
        ) % len(self.WALL_COLORS)
        self.redraw()

    def handle_key(self, keycode: int) -> None:
        """Apply the interaction assigned to a released key."""
        if keycode == ord("1"):
            self.regenerate()
        elif keycode == ord("2"):
            self.toggle_path()
        elif keycode == ord("3"):
            self.rotate_wall_color()
        elif keycode in (ord("4"), ord("q"), 65307):
            self.stop()

    def stop(self) -> None:
        """Request that the MLX event loop returns."""
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def cleanup(self) -> None:
        """Release every MLX resource once, in reverse creation order."""
        if self._cleaned_up:
            return
        self._cleaned_up = True
        if getattr(self, "img_ptr", None):
            self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
            self.img_ptr = None
        if getattr(self, "win_ptr", None):
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
            self.win_ptr = None
        if getattr(self, "mlx_ptr", None):
            self.mlx.mlx_release(self.mlx_ptr)
            self.mlx_ptr = None

    def run(self) -> None:
        """Draw the maze, register events and enter the MLX event loop."""
        self.mlx.mlx_key_hook(self.win_ptr, _on_key, self)
        self.mlx.mlx_expose_hook(self.win_ptr, _on_expose, self)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, _on_close, self)
        self.redraw()
        try:
            self.mlx.mlx_loop(self.mlx_ptr)
        finally:
            self.cleanup()


def _on_key(keycode: int, renderer: MazeRenderer) -> None:
    """MLX callback for released keyboard keys."""
    try:
        renderer.handle_key(keycode)
    except Exception as error:
        print(f"Rendering error: {error}")
        renderer.stop()


def _on_expose(renderer: MazeRenderer) -> None:
    """MLX callback used when the window asks to be redrawn."""
    try:
        renderer.redraw()
    except Exception as error:
        print(f"Rendering error: {error}")
        renderer.stop()


def _on_close(renderer: MazeRenderer) -> None:
    """MLX callback for the window manager's close request."""
    renderer.stop()
