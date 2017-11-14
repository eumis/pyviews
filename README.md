# pyviews

## About
### Description
Package adds ability to create ui by declarative way using tkinter

### Features
* Widgets creation is described in xml files
* One way and two ways binding
* Fully customizable via dependency injection

## Code
### Repository structure
* pyviews - source code
* sandbox - sample app with using pyviews
* tests - unit tests

### Running tests
Tests are implemented with package unittest.
To run all tests execute following command

`python -m unittest discover -s {project_root}\\tests -v -p *_test.py`

### Running sandbox app
Run following command to install pyviews package

`pip install {project_root}`

Run run.py with python. Working directory should be sandbox folder

`python run.py`

## Key concepts
Xml namespaces are interpreted as modules. Tags are interpreted as classes that need to be instantiated.

```xml
<Frame xmlns='tkinter'>
</Frame>
```
Also here we can encapsulate different functionality in node.
```xml
<Frame xmlns='tkinter'
       xmlns:w='pyviews.tk.widgets'>
       <w:For items='{list(range(10))}'>
            <Label />
       </w:For>
</Frame>
```
In this case widget is not created for tag `<w:For />`. Logic with creating 10 labels inside frame implemented in class that represents this tag.
```xml
<Frame xmlns='tkinter'
       xmlns:w='pyviews.tk.widgets'>
       <w:For items='{list(range(10))}'>
            <Label text='{str(item)}'/>
       </w:For>
</Frame>
```
### Code structure
There are two packages under root packages
#### core

#### tk
