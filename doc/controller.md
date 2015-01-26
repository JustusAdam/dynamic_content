# Controller functions

## How it operates

Websites in dynamic_content are created using a html template, also called 'view' and a function called the controller function or controller method which supplies the dynamic context/values for the template parser.

The frameworks backbone data structure called 'DynamicContent' glues these two together.

## The decorator

Functions operating as a controller in dynamic_content are marked as such using a python decorator.

### Name and location

The decorator is called `@controller_function()` or `@controller_method()` if your controller function is a method of a class and not a bare function.

**Important**: If you are using a method as a controller the class containing the method has to be annotated as `@controller_class` or your controller will not be registered.

The decorator is located in the package `dyc.core.mvc(.decorator)`.

This decorator then has to be supplied with configuration information. Which pages that this controller wished to handle and how it is to be handled.

**Important**: Usually this decorator is (has to be) the top-most decorator that is applied to the function since decorators resolve inside out, meaning any decorator applied above the `@controller_function` decorator has no effect on the in/output when the framework calls controller function.

More that one of these decorators can be applied to the same function.

### Parameters

The full function signature is (the same signature applies to `controller_method`):

```python
def controller_function(
value,
*,
method=dchttp.RequestMethods.GET,
headers=None,
query=False,
**options
):
```

Name | Type | default | Function
-----|------|---------|----------
value | str, set[str] | no default | paths that this controller function handles
method | str, set[str] | 'get' | types of request methods this controller function handles
headers | str, set[str] | None | special headers a request must have to be handled by this controller (None=no special headers) (does not work yet)
query | bool, list[str], tuple[str], dict{str: str} | False | either marks whether this controller accepts a query **or** which query parameters this function wants and in the case of the dict, how they should be called
options | any | no options | additional options that are attached to the resulting ControllerFunction (attribute 'options') and can be accessed by view middleware

### Path parameters

When specifying a path for a controller function/method you can utilize a special minilanguage to handle dynamic paths.

Path parameters are enclosed in curly braces '{}' and can either be just types or types and an argument name separated by a space (`{str}`, `{int}`, `{int number}`, `{str name}`).

When the controller function is called the current path gets matched against these parameters and the math values are given as arguments to the controller. Unnamed parameters are supplied as positional arguments in the order they appear in the path aka `/hello/you/my/4` when matched with `/hello/{str}/my/{int}` will yield `'you', 4`. Named parameters are supplied as keyword arguments where the parameter name is the argument name aka `/hello/you/my/4` matched with `/hello/{str name}/my/{int}` yields `4, name='you'`.

Currently supported types are `str` and `int` (support for `float` and `hex` is planned in the future)

Path parameters have to be an entire path section aka `/some/{str}/hello`, there is no support for partial parameters aka `some/either-{str}/hello` yet. However you can use as many path parameters as you like and switch between named and unnamed path parameters.

### Queries

Your controller function can express its desire to accept a query in three different ways. Depending on the type of the argument supplied to `query=` in the decorator.

Type | Effect | value type (when calling the controller) | argument type (when calling the controller)
-----|--------|------------------------------------------|----------------------------------------------
bool | toggles whether to supply the (full) query to the controller function | `dict[str, list]` | positional
iterable[str] | names of arguments to filter the query for | `list, list, ...` | keyword argument, (argument names are the names in the supplied iterable)
dict[str, str] | keys are names to filter the query for | `list, list, ...` | keyword argument, (argument names are the corresponding dict values)
str | name to filter the query for | `list` | special case of iterable[str] for single argument



### Example

```python
from dyc.core import mvc
from dyc import dchttp

# defining a controller function
@mvc.controller_function(
    {'greeting/hello', 'greeting/hola'}, # set of paths to handle
    method=dchttp.RequestMethods.GET, # method to handle
    query=False # we dont want a query
)
def my_controller(dc_obj):
    dc_obj.context['title'] = "Greeting"
    dc_obj.context['greeting'] = "Whoever you are"
    return "greeting" # returning the view name

# defining a controller method
@mvc.controller_class
class MyController(object):
    @mvc.controller_method(
        'hello/{str}', # we can specify a path with a string instead of a set
        method=dchttp.RequestMethods.POST, # lets handle some post requests
        query=['city', 'street'],
        anti_csrf=False, # one of the **options, this one turns csrf checking off
        force_ssl=True # another **option, this one will force ssl, if available
    )
    def my_method(self, dc_obj, path_arg, city, street):
        # do stuff
        return ':redirect:/somewhere'

```

### Implementation details

1. The actual signature of the decorator is obscured, since it is only a partially applied function. The real decorator is called `_controller_function`/`_controller_method` and additionally takes a type as a first argument.
    An instance of that type is registered with the pathmapper when the decorator registers the controller.

    ```python
    def _controller_function(
        class_,
        value,
        *,
        method=dchttp.RequestMethods.GET,
        headers=None,
        query=False,
        **options
        ):
    ```
* `@controller_method` does not return the original function but rather a callable instance of dyc.core.mvc.decorator.ControllerFunction.

## Structure

Any function that handles a view requires a specific signature that depends on the options chosen in the decorator.

### Common Signature

Any normal controller function has the following base signature:

```python
@controller_function(**options)
def controller_f(dc_obj, *args, **kwargs):
    dc_obj # instance of dyc.util.structures.DynamicContent
    return "" # view name
```
