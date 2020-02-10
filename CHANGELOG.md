# Changelog

## Dev

- updated injectool up to 2.0.1
- run_steps() function is moved to RenderingPipeline as run() method
- create_node() function is part of RenderingPipeline
- RenderingPipeline is resolved by xml namespace and tag
- render() returns observable
- get_inst_type() renamed to get_type()
- create_inst() renamed to create_instance()
- Rendering steps are renamed to pipes. Common pipes module is moved to core
- Common setters module is moved to core
- modifier is renamed to setter
- Removed CompiledExpression class
- Expression class is moved to compilation package and removed ABC inheritance
- added execute() function to compilation package
- removed injection of Expression class
- CoreError is renamed to ViewsError
- removed Node.properties and Property class
- updated error message for resolving RenderingPipeline
- added Args class to pass args to call setter
- added inline binding

## 2.3.0

- **args are changed to RenderingContext for rendering steps
- **args are changed to BindingContext for binding
- ObjectNode is changed to named tuple
- XmlNode and XmlAttr are changed to named tuples
- RenderingPipeline is changed to  tuple 
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
