# Changelog

## 4.0.0

- upgraded injectool to 3.0.0
- Observable is renamed to Bindable
- expression is moved to core
- expression binding is refactored
- InheritedDict is renamed to BindableDict
- Added NodeGlobals class
- setup modules are renamed to config
- added parse function to core xml module

## 3.2.0

- added BindingNode
- added inject binding
- added expression bindings for indexes like "vm[0].attr" or "vm[index.value].attr"
- RenderingPipeline is made generic

## 3.1.0

- added containers(Container, View, If, For)
- added presenter
- added pipeline name to display in error info
- added getting current rendering context

## 3.0.1

- added use_rendering() and use_pipeline()
- added use_binding()

## 3.0.0

- updated injectool up to 2.0.1
- RenderingPipeline is resolved by xml namespace and tag
- create_node() function is part of RenderingPipeline
- run_steps() function is moved to RenderingPipeline as run() method
- Rendering steps are renamed to pipes. Common pipes module is moved to core
- removed Node.properties and Property class
- Node.set_attr method is removed. Node.attr_setter property is renamed to set_attr
- "compilation" package is renamed to "expression"
- Expression class is moved to compilation package and removed ABC inheritance
- removed injection of Expression class
- Removed CompiledExpression class
- execute method from Expression is changed to function and can be used as dependency
- modifier is renamed to setter
- Common setters module is moved to core
- added Args class to pass args to call setter
- BindingRule class is changed to tuple
- BindingTarget class is removed. BindingCallback is used instead.
- Added inline binding
- CoreError is renamed to PyViewsError
- added error_handling() function
- Changed error output format
- removed predefined namespaces

## 2.3.0

- **args are changed to RenderingContext for rendering steps
- **args are changed to BindingContext for binding
- ObjectNode is changed to named tuple
- XmlNode and XmlAttr are changed to named tuples
- RenderingPipeline is changed to tuple
- pyviews.core.rendering module is removed
- create_node and render dependencies are moved to pyviews.rendering

## 2.2.0

- Expression resolved using code as resolve parameter
- Migrated to injectool 1.1.1

## 2.1.1

- changed call setter

## 2.1.0

- added call setter
- updated modules structure
- used pytest for unit tests
- ioc module is moved to separate package [injectool](https://github.com/eumis/injectool)
