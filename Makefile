PYTHON := python3

MLX_ARCHIVE := mlx.tgz
MLX_DIR := .mlx

CONFIG := config.txt
MAIN := a_maze_ing.py

.PHONY: install run debug clean fclean re lint lint-strict build


install:
	$(PYTHON) -m pip install -e ".[dev]"
	@mkdir -p $(MLX_DIR)
	@tar -xzf $(MLX_ARCHIVE) -C $(MLX_DIR)
	@if [ "$$(uname -s)" = "Linux" ]; then \
		if grep -qi "ubuntu" /etc/os-release; then \
			echo "Installing MLX for Ubuntu..."; \
			$(PYTHON) -m pip install \
				$(MLX_DIR)/ubuntu/mlx-2.2-py3-none-any.whl; \
		elif grep -qi "fedora" /etc/os-release; then \
			echo "Installing MLX for Fedora..."; \
			$(PYTHON) -m pip install \
				$(MLX_DIR)/fedora/mlx-2.2-py3-none-any.whl; \
		else \
			echo "Error: unsupported Linux distribution for supplied MLX."; \
			exit 1; \
		fi; \
	elif [ "$$(uname -s)" = "Darwin" ]; then \
		echo "macOS detected."; \
		echo "The supplied mlx.tgz contains Ubuntu/Fedora wheels."; \
		echo "Using the MLX installation already available on this system."; \
	else \
		echo "Error: unsupported operating system."; \
		exit 1; \
	fi


run:
	$(PYTHON) $(MAIN) $(CONFIG)


debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)


lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs


lint-strict:
	flake8 .
	mypy . --strict


build:
	$(PYTHON) -m build


clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf $(MLX_DIR)
	rm -rf build
	rm -rf *.egg-info
	rm -rf mazegen.egg-info


fclean: clean
	rm -rf dist


re: fclean install
