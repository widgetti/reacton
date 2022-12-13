# Testing

Testing can be done by explictly rendering, and checking the `ipywidgets` that Reacton produces.

```python
import reacton
import ipywidgets as widgets
import reacton.ipywidgets as w

def test_docs_example():
    set_state = None

    @react.component
    def Test():
        nonlocal set_state
        state, set_state = react.use_state(0)
        if state == 0:
            return w.Button(description="Hi")
        else:
            return w.FloatSlider()

    box, rc = react.render(Test(), handle_error=False)
    assert isinstance(box.children[0], widgets.Button)
    assert set_state is not None
    set_state(1)

    assert isinstance(box.children[0], widgets.FloatSlider)
```

This can become tiresome, and we have a playwright-like API to find widgets:
```python
    ...
    # usind the find api
    rc.find(widgets.FloatSlider).assert_single()
    rc.find(widgets.Button).assert_empty()
    set_state(0)
    rc.find(widgets.FloatSlider).assert_empty()
    rc.find(widgets.Button).assert_single()
```

Or be more specific about matching properties:
```python
    ...
    rc.find(widgets.Button, description="Hello").assert_empty()
    rc.find(widgets.Button, description="Hi").assert_single()
```

## Tagging elements/widgets

Often, you just want to know if a widget is rendered, or you want to find a widget very deep into you application tree. In those cases, we can attach meta data to the widget, and query based on that:

```python
def test_docs_example_meta():
    @react.component
    def Test():
        # add {'meta': 'ref'} to the widget
        return w.Button(description="1").meta(ref="some_button")

    box, rc = react.render(Test(), handle_error=False)
    # we just want to know, did it render?
    rc.find(meta_ref="some_button").assert_single()
```

## Async support


In you need to wait for UI changes, because some work is being done in a thread, use `.wait_for()`:

```python
import reacton
import time
import threading

def test_docs_example_async():
    @react.component
    def Test():
        state, set_state = react.use_state(0)

        def thread_run():
            time.sleep(0.5)
            set_state(1)

        reacton.use_effect(lambda: threading.Thread(target=thread_run).run(), [])

        if state == 0:
            return w.Button(description="Hi")
        else:
            return w.FloatSlider()

    box, rc = react.render(Test(), handle_error=False)
    rc.find(widgets.FloatSlider).wait_for().assert_single()
```

## Examples

All of these examples can be found in the tests of Reacton itself, don't be afraid to read the test code:

  * https://github.com/widgetti/reacton/blob/master/reacton/find_test.py
  * https://github.com/widgetti/reacton/blob/master/reacton/core_test.py
