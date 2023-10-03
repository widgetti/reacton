from IPython.core.formatters import BaseFormatter
from IPython.core.interactiveshell import InteractiveShell


def publish(data, metadata=None, *args, **kwargs):
    """Will intercept a display call and add the display data to an output widget when in a reacton context/render function."""
    from .core import get_render_context

    assert original_display_publisher_publish is not None

    rc = get_render_context(required=False)
    # only during the render phase we want to capture the display calls
    # during the reconsolidation phase we want to let the original display publisher do its thing
    # such as adding it to a output widget
    if rc is not None and not rc.reconsolidating:
        from .ipywidgets import Output

        Output(outputs=[{"output_type": "display_data", "data": data, "metadata": metadata}])
    else:
        return original_display_publisher_publish(data, metadata, *args, **kwargs)


class ReactonDisplayFormatter(BaseFormatter):
    """Add direct support for adding elements to a container.

    Example:

    with w.VBox():
        display(button)

    """

    def __call__(self, obj):
        assert ipython_display_formatter_original is not None
        from .core import Element, get_render_context  # noqa

        rc = get_render_context(required=False)
        if rc is not None:
            if rc.container_adders:
                if isinstance(obj, Element):
                    # add directly as a child
                    rc.container_adders[-1].add(obj)
                    return True  # we handled it
        return ipython_display_formatter_original(obj)


patched = False
ipython_display_formatter_original = None
original_display_publisher_publish = None


def patch():
    global patched, ipython_display_formatter_original, original_display_publisher_publish
    if patched:
        return
    patched = True
    shell = InteractiveShell.instance()
    ipython_display_formatter_original = shell.display_formatter.ipython_display_formatter  # type: ignore
    original_display_publisher_publish = shell.display_pub.publish
    assert shell.display_formatter is not None
    shell.display_formatter.ipython_display_formatter = ReactonDisplayFormatter()  # type: ignore
    shell.display_pub.publish = publish  # type: ignore


if InteractiveShell.initialized():
    patch()
