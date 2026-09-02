.PHONY: install run debug clean lint lint-strict build mlx-setup

MLX_ARCHIVE := mlx-2.2.tgz

install: mlx-setup
	pip install -r requirements.txt

mlx-setup:
	@if [ -f $(MLX_ARCHIVE) ]; then \
		tar -xzf $(MLX_ARCHIVE); \
		if [ -f /etc/os-release ] && grep -qi ubuntu /etc/os-release; then \
			echo "Detected Ubuntu, installing ubuntu wheel..."; \
			pip install ubuntu/mlx-2.2-py3-none-any.whl; \
		elif [ -f /etc/os-release ] && grep -qi fedora /etc/os-release; then \
			echo "Detected Fedora, installing fedora wheel..."; \
			pip install fedora/mlx-2.2-py3-none-any.whl; \
		else \
			echo "Could not detect OS, defaulting to ubuntu wheel..."; \
			pip install ubuntu/mlx-2.2-py3-none-any.whl; \
		fi \
	else \
		echo "Warning: $(MLX_ARCHIVE) not found, skipping MLX setup"; \
	fi

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

clean:
	find . -path ./.venv -prune -o -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache
	rm -rf build/ dist/ *.egg-info
	rm -rf ubuntu/ fedora/ src/

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	python3 -m build
