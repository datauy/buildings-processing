#!/bin/bash

# Set python version and venv name
export PYTHON_VERSION=3.10.7
export PYTHON_VENV=dencity_3.10.7

echo "Installing Python $PYTHON_VERSION..."
pyenv install $PYTHON_VERSION
pyenv local $PYTHON_VERSION

echo "Setting python shell..."
pyenv shell $PYTHON_VERSION

echo "Creating virtual environment..."
pyenv virtualenv $PYTHON_VENV

echo "Activating virtual environment..."
pyenv activate $PYTHON_VENV

echo "Upgrade pip"
pip install --upgrade pip

echo "Installing development Python libraries"
pip install black isort flake8

echo "Done!"