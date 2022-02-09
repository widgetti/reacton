# React for ipywidgets

Making writing Web based UI from Python, using ipywidgets, easier, fun and without bugs.

## What is it?

A way to write reusable components in a React like way, to make Python based UI's using the ipywidgets ecosystem (ipywidgets, ipyvolume, bqplot, threejs, leaflet, ipyvuetify, ...).

## Why ? What is the problem?

Non-declerative UI's are hard, you have to attach and detatch event handlers at the right point. There are many possibles states your UI can be in, and moving from one state to the other can be very hard to do manually, and is very error prone.

A common issue we also see, is that there is one piece of code to set up the UI, and scattered around in many event handler the changes that are almost repetitions of the initialization code.

## Why using a React solution

Using a declerative way, in a React (JS) style, makes your codebase smaller, less error prone, and easier to reason about. We don't see a good reason *not* to use it.

Also, React has proven itself, and by adopting a proven technology we can stand on the shoulders of smart people, make use of a lot of existing resources, and do not have to reinvent the wheel.

## What does react-ipywidgets do for me?

Instead of telling ipwidgets what to do, e.g.:

  * Respond to events
  * Changing properties
  * Attaching and detaching event handlers

You tell react-ipywidgets what you want (which Widgets you want to have), and you let react-ipywidgets take care of the above.

## Simple example

### Using plain ipywidgets

Take for example this simple example of a button that counts the number of clicks
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
   * There is not good place/namespace to store the `clicks` variables, did the `global` trigger you?
   * This code is in no way re-useble / composable.

Nothing that can be solved, but the burden is on you to come up with solutions.

### Using react-ipywidgets

If we solve the same problem using react-ipywidgets, we create (like ReactJS) a reusable component that describes the widgets we want, and it's up to `react_ipywidgets` to show/update/modify the widget in an efficient way.

Using `react.use_state` we explicitly say we need a piece of local state, that we initialize it to 0. Using `on_click` your event handler will be attached and detached when needed, and your function will be re-executed when the state changes (the click count).

```python
import react_ipywidgets as react
import react_ipywidgets.ipywidgets as w

@react.component
def ButtonClick(label="Hi"):
    clicks, set_clicks = react.use_state(0)
    return w.ButtonWithClick(description=f"{label}: Clicked {clicks} times",
                             on_click=lambda: set_clicks(clicks+1))
ButtonClick()
```

We now have a simple component that we can reuse, e.g. like this:
```python
@react.component
def ManyButtons(count=10):
    count, set_count = react.use_state(count)
    slider = w.IntSlider(min=0, max=20, value=count, on_value=set_count)
    buttons = [ButtonClick(f"Hi-{i}") for i in range(count)]
    return w.VBox(children=[slider, *buttons])
ManyButtons()
```

We take care of not re-creating new Buttons widgets all the time (which is relatively expensive). We reuse existing widgest when we can, and create new ones when needed.

*Try creating the `ManyButtons` component without using ipywidgets, and you will really appriciate react-ipywidgets*

# Installation
## User

Most users:

    $ pip install react_ipywidgets

Conda users:

    $ conda install -c conda-forge innstall react_ipywidgets


## Development

We use flit (`pip install flit` if you don't already have it)

    $ flit install --symlink --deps develop
