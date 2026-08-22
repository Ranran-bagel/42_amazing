class MazeError(Exception):
    pass

class ConfigError(MazeError):
    pass

class MazeGenerationError(MazeError):
    pass

class OutputError(MazeError):
    pass