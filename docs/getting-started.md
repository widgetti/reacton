
## Getting started

Put this in the Jupyter notebook:

```py
import reacton
import reacton.ipywidgets as w

@reacton.component
def ButtonClick():
    clicks, set_clicks = reacton.use_state(0)
    def my_click_handler():
        set_clicks(clicks+1)
    button = w.Button(description=f"Clicked {clicks} times",
                      on_click=my_click_handler)
    return button
```

Make the last expression of your cell:

```py
ButtonClick()
```

Or explicitly display it using:

```py
el = ButtonClick
display(el)
```
