[![Documentation](https://readthedocs.org/projects/react-ipywidgets/badge/?version=latest)](https://reacton.solara.dev/)
[![Jupyter Lab](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://reacton.solara.dev/en/latest/_output/lab/index.html)

# Reacton: React for ipywidgets

Write ipywidgets like Reacton. Creating a Web-based UI from Python, using ipywidgets made easier, fun, and without bugs.

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

clicks = 0
def on_click(button):
    global clicks
    clicks += 1
    button.description = f"Clicked {clicks} times"
button = widgets.Button(description="Clicked 0 times")
button.on_click(on_click)
display(button)
```

We see the following issues:

   * The button description text is repeated twice (once for initialization at `"Clicked 0 times"` and once in the event handler `f"Clicked {clicks} times"`)
   * An event handler is attached, which we need to detach if we do not want to leak resources
   * There is no good place/namespace to store the `clicks` variables, did the `global` trigger you?
   * This code is in no way re-useable / composable.

These issues can be solved, but the burden is on you to come up with solutions.

### Using reacton

If we solve the same problem using reacton, we create (like ReactJS) a reusable component that describes the widgets we want, and it's up to `reacton` to show/update/modify the widget in an efficient way.

Using `reacton.use_state`, we explicitly say we need a piece of local state, with an initialize value of `0`. Using `on_click`, your event handler will be attached and detached when needed, and your function will be re-executed when the state changes (the click count).

```python
import reacton
import reacton.ipywidgets as w

@reacton.component
def ButtonClick(label="Hi"):
    clicks, set_clicks = reacton.use_state(0)
    return w.Button(description=f"{label}: Clicked {clicks} times",
                    on_click=lambda: set_clicks(clicks+1))
ButtonClick()
```

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

We take care of not re-creating new Buttons widgets (which is relatively expensive). We reuse existing widgets when we can and create new ones when needed.

*Try creating the `ManyButtons` component without using pure ipywidgets, and you will really appreciate reacton*


## Markdown component example

Given this [suggestion](https://github.com/jupyter-widgets/ipywidgets/issues/2428#issuecomment-500084610) on how to make a widget with markdown, we don't have an obvious path forward to create a new Markdown widget that can be reused. Should we inherit? From which class? Should we compose and inherit from VBox or HBox and add the HTML widget as a single child?

With react-ipywidgest there is an obvious way:
```python
@reacton.component
def Markdown(md: str):
    from myst_parser.main import to_html
    html = to_html(md)
    return w.HTML(value=html)
```

This `Markdown` component can now be reused to create a markdown editor:

```python
@reacton.component
def MarkdownEditor(md : str):
    md, set_md = reacton.use_state(md)
    with w.VBox() as main:
        w.Textarea(value=md, on_value=set_md)
        Markdown(md)
    return main

display(MarkdownEditor("Mark-*down* **component**"))
```

The `MarkdownEditor` component also shows another feature we can provide: All container widgets (like HBox, VBox, and all ipyvuetify widgets) can act as a context manager, which will add all widgets elements created within it as its children. Using a context manager leads to better readable code (less parenthesis and parenthsis issues).

# Documentation


[![Documentation](https://readthedocs.org/projects/reacton/badge/?version=latest)](https://reacton.solara.dev/)


## Examples

API documentation is great, but like writing, you learn by reading.

Our example notebooks can be found at:

   * [https://github.com/widgetti/reacton/tree/master/notebooks](https://github.com/widgetti/reacton/tree/master/notebooks)


Or try them out directly in a Jupyter environment (JupyterLite)

   * [![Jupyter Lab](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://reacton.solara.dev/en/latest/_output/lab/index.html)

Direct link to examples:

   * [ButtonClick](https://reacton.solara.dev/en/latest/_output/lab/index.html?path=click-button.ipynb)
   * [Calculator](https://reacton.solara.dev/en/latest/_output/lab/index.html?path=calculator.ipynb)
   * [Todo-app](https://reacton.solara.dev/en/latest/_output/lab/index.html?path=todo-app.ipynb)


# Installation
## User

Most users:

    $ pip install reacton

Conda users (not yet):

    $ conda install -c conda-forge install reacton


## Development

To get an editable install, use the `-e` flag.

    $ pip install -e .
