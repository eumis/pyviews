# About
## Description
Package adds ability to create ui by declarative way using tkinter

## Features
* Widgets creation is described in xml files
* One way and two ways bindings
* Fully customizable via dependency injection

## Installation
`pip install git+https://yauheni_m@bitbucket.org/yauheni_m/pyviews.git@dev`

# Code
## Repository structure
* pyviews - source code
* sandbox - sample app with using pyviews
* tests - unit tests

## Running tests
Tests are implemented with package unittest.
To run all tests execute following command

`python -m unittest discover -s {project_root}\\tests -v -p *_test.py`

## Running sandbox app
Run following command to install pyviews package

`pip install {project_root}`

Run run.py with python. Working directory should be sandbox folder

`python run.py`