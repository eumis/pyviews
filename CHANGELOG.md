# Changelog

## Dev

- updated injectool up to 2.0.1
- run_steps() function is moved to RenderingPipeline as run() method
- create_node() function is made part of RenderingPipeline
- RenderingPipeline is resolved by xml namespace and tag
- Added RenderingIterator
- Rendering steps are renamed to pipes. Common pipes module is moved to core
- Common modifiers module is moved to core
- Removed CompiledExpression class
- Expression class is moved to compilation package and removed ABC inheritance
- added execute() function to compilation package
- removed injection of Expression class

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

- changed call modifier

## 2.1.0

- added call modifier
- updated modules structure
- used pytest for unit tests
- ioc module is moved to separate package [injectool](https://github.com/eumis/injectool)
