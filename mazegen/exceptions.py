class MazeError(Exception):
    pass


class ConfigError(MazeError):
    pass


class MazeGenerationError(MazeError):
    pass


class PatternError(MazeGenerationError):
    pass


class OutputError(MazeError):
    pass
