[![Documentation](https://readthedocs.org/projects/react-ipywidgets/badge/?version=latest)](https://reacton.solara.dev/)
[![Jupyter Lab](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://reacton.solara.dev/en/latest/_output/lab/index.html)

# Reacton: React for ipywidgets

Write ipywidgets like Reacton. Creating a Web-based UI from Python, using ipywidgets made easier, fun, and without bugs.

![logo](https://user-images.githubusercontent.com/1765949/207259505-077acebd-1d74-4273-abf5-3a0226c03efd.png)

## What is it?

A way to write reusable components in a React-like way, to make Python-based UI's using the ipywidgets ecosystem (ipywidgets, ipyvolume, bqplot, threejs, leaflet, ipyvuetify, ...).

## Why? What is the problem?

Non-declarative UI's are complex: You have to attach and detach event handlers at the right point, there are many possibles states your UI can be in, and moving from one state to the other can be very hard to do manually and is very error-prone.

Using Reacton, you write a component that gives a declarative description of the UI you want based on data. If the data changes, your component render function re-executes, and Reacton will find out how to go from the previous state to the new state. No more manual "diffing" on the UI, no more manual tracking of which event handlers to attach and detach.

A common issue we also see is that there is one piece of code to set up the UI, and scattered around in many event handlers the changes that are almost repetitions of the initialization code.

## Why use a React-like solution

Using a declarative way, in a React (JS) style, makes your codebase smaller, less error-prone, and easier to reason about. We don't see a good reason *not* to use it.

Also, React has proven itself, and by adopting a proven technology, we can stand on the shoulders of giants, make use of a lot of existing resources, and do not have to reinvent the wheel.

## What does Reacton do for me?

Instead of telling ipywidgets what to do, e.g.:

  * Responding to events.
  * Changing properties.
  * Attaching and detaching event handlers.
  * Adding and removing children.
  * Manage widget lifetimes (creating and destroying).

You tell reacton what you want (which Widgets you want to have), and you let reacton take care of the above.

## Installing

```bash
$ pip install reacton
```
## Simple example

### Using plain ipywidgets

Take, for example, this simple example of a button that counts the number of clicks
```python
import ipywidgets as widgets

clicks = 0  # issue 3
def on_click(button):
    global clicks  # issue 3
    clicks += 1
    button.description = f"Clicked {clicks} times"     # issue 1
button = widgets.Button(description="Clicked 0 times") # issue 1
button.on_click(on_click)  # issue 2
display(button)
```
![Button with counter - bad](https://user-images.githubusercontent.com/1765949/207260036-9aba0b23-1783-4fea-ade4-216c6aabc8c6.gif)

We see the following issues:

 1. The button description text is repeated in two places (initialization and the event handler).
 2. An event handler is attached, but without a defined life cycle, it can be difficult to know when to detach it to avoid memory leaks.
 3. The "clicks" variable is stored in the global scope, which may be concerning for some developers.
 4. The code is not easily reusable or composable.

These issues can be solved, but the burden is on you to come up with solutions.

### Using Reacton

If we solve the same problem using reacton, we create (like ReactJS) a reusable component that describes the widgets we want, and it's up to `reacton` to show/update/modify the widget in an efficient way.

Using `reacton.use_state`, we explicitly say we need a piece of local state, with an initial value of `0`. Using `on_click`, your event handler will be attached and detached when needed, and your function will be re-executed when the state changes (the click count).

```python
import reacton
import reacton.ipywidgets as w


@reacton.component
def ButtonClick():
    # first render, this return 0, after that, the last argument
    # of set_clicks
    clicks, set_clicks = reacton.use_state(0)

    def my_click_handler():
        # trigger a new render with a new value for clicks
        set_clicks(clicks+1)

    button = w.Button(description=f"Clicked {clicks} times",
                      on_click=my_click_handler)
    return button

ButtonClick()
```
![Button with counter using Reacton](https://user-images.githubusercontent.com/1765949/207261815-c41c1dbf-6d8a-4741-863b-b84c43b657a6.gif)

We now have a simple component that we can reuse, e.g., like this:
```python
@reacton.component
def ManyButtons(count=10):
    count, set_count = reacton.use_state(count)
    slider = w.IntSlider(min=0, max=20, value=count, on_value=set_count)
    buttons = [ButtonClick(f"Hi-{i}") for i in range(count)]
    return w.VBox(children=[slider, *buttons])
display(ManyButtons())
```
![Many buttons](https://user-images.githubusercontent.com/1765949/207262265-56052f1b-0cc3-42aa-8c35-bf10650c8514.gif)

We take care of not re-creating new Buttons widgets (which is relatively expensive). We reuse existing widgets when we can and create new ones when needed.

*Try creating the `ManyButtons` component without using pure ipywidgets, and you will really appreciate reacton*


## Markdown component example

Given this [suggestion](https://github.com/jupyter-widgets/ipywidgets/issues/2428#issuecomment-500084610) on how to make a widget with markdown, we don't have an obvious path forward to create a new Markdown widget that can be reused. Should we inherit? From which class? Should we compose and inherit from VBox or HBox and add the HTML widget as a single child?

With Reacton there is an obvious way:
```python
import reacton
import markdown
import reacton.ipywidgets as w


@reacton.component
def Markdown(md: str):
    html = markdown.markdown(md)
    return w.HTML(value=html)

display(Markdown("# Reacton rocks\nSeriously **bold** idea!"))
```

This `Markdown` component can now be reused to create a markdown editor:

```python
@reacton.component
def MarkdownEditor(md : str):
    md, set_md = reacton.use_state(md)
    edit, set_edit = reacton.use_state(True)
    with w.VBox() as main:
        Markdown(md)
        w.ToggleButton(description="Edit",
                       value=edit,
                       on_value=set_edit)
        if edit:
            w.Textarea(value=md, on_value=set_md, rows=10)
    return main
display(MarkdownEditor("# Reacton rocks\nSeriously **bold** idea!"))
```
![Markdown component and editor](https://user-images.githubusercontent.com/1765949/207259602-e671087f-67bf-41b3-81ee-27730c0693df.gif)

The `MarkdownEditor` component also shows another feature we can provide: All container widgets (like HBox, VBox, and all ipyvuetify widgets) can act as a context manager, which will add all widgets elements created within it as its children. Using a context manager leads to better readable code (less parenthesis and parenthsis issues).

# Documentation


[![Documentation](https://readthedocs.org/projects/react-ipywidgets/badge/?version=latest)](https://reacton.solara.dev/)


## Examples

API documentation is great, but like writing, you learn by reading.

Our example notebooks can be found at:

   * [https://github.com/widgetti/reacton/tree/master/notebooks](https://github.com/widgetti/reacton/tree/master/notebooks)


Or try them out directly in a Jupyter environment (JupyterLite)

   * [![Jupyter Lab](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://reacton.solara.dev/en/latest/_output/lab/index.html)

Direct link to examples:

   * [ButtonClick](./_output/lab/index.html?path=click-button.ipynb)
     ![Button with counter](https://user-images.githubusercontent.com/1765949/207259596-42cedcf1-d671-4e47-827d-fff9aaea55a6.gif)
   * [Calculator](./_output/lab/index.html?path=calculator.ipynb)
     ![Calculator](https://user-images.githubusercontent.com/1765949/207259600-aacc4d6f-edec-4f52-9f26-d730a6332db2.gif)
   * [Todo-app](./_output/lab/index.html?path=todo-app.ipynb)
     ![Todo app](https://user-images.githubusercontent.com/1765949/207259603-cc1222ec-d3db-4905-967d-b1401bb9697c.gif)
   * [Markdown](./_output/lab/index.html?path=markdown.ipynb)
     ![Markdown component and editor](https://user-images.githubusercontent.com/1765949/207259602-e671087f-67bf-41b3-81ee-27730c0693df.gif)


# Installation
## User

Most users:

    $ pip install reacton

Conda users:

    $ conda install -c conda-forge install reacton


## Development

To get an editable install, use the `-e` flag.

    $ pip install -e .
