# Makefile

# Define the Python interpreter and virtual environment directory
PYTHON := python3
VENV_DIR := venv

# Define directories
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs
DOCS_SRC_DIR := docs/source

# Docker image name
IMAGE_NAME := jobs_data_analysis

# Define the path to the requirements file
REQUIREMENTS := requirements.txt

# Mark venv as a phony target
.PHONY: venv
# Create a virtual environment and install dependencies
venv:
	@if [ -d "$(VENV_DIR)" ]; then rm -rf $(VENV_DIR); fi
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

# Mark format as a phony target
.PHONY: format
# Format code with Black
format: venv
	$(VENV_DIR)/bin/black $(SRC_DIR) $(TEST_DIR)

# Mark test as a phony target
.PHONY: test
# Run pytest
test: venv
	$(VENV_DIR)/bin/pytest $(TEST_DIR)

# Mark build as a phony target
.PHONY: build
# Build the Docker image
build: format test
	docker build -t $(IMAGE_NAME) .

# Mark clean as a phony target
.PHONY: clean
# Clean up Python cache files
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +

# Mark run as a phony target
.PHONY: run
# Run the Docker container
run:
	docker run --rm $(IMAGE_NAME)

# Mark docs as a phony target
.PHONY: docs
# Generate Sphinx documentation
docs: venv
	$(VENV_DIR)/bin/sphinx-apidoc -o $(DOCS_SRC_DIR) $(SRC_DIR)
	$(MAKE) -C $(DOCS_DIR) html

# Mark all as a phony target
.PHONY: all
# Target to perform all necessary steps: clean, set up venv, format, test and build
all: clean venv format test build
