from IPython.core.formatters import BaseFormatter
from IPython.core.interactiveshell import InteractiveShell

ipython_display_formatter_original = InteractiveShell.instance().display_formatter.ipython_display_formatter
original_display_publisher_publish = InteractiveShell.instance().display_pub.publish


def publish(data, metadata=None, *args, **kwargs):
    """Will intercept a display call and add the display data to an output widget when in a reacton context/render function."""
    from .core import get_render_context

    rc = get_render_context(required=False)
    if rc is not None:
        from .ipywidgets import Output

        Output(outputs=[{"output_type": "display_data", "data": data, "metadata": metadata}])
    else:
        original_display_publisher_publish(data, metadata, *args, **kwargs)


class ReactonDisplayFormatter(BaseFormatter):
    """Add direct support for adding elements to a container.

    Example:

    with w.VBox():
        display(button)

    """

    def __call__(self, obj):
        from .core import Element, get_render_context  # noqa

        rc = get_render_context(required=False)
        if rc is not None:
            if rc.container_adders:
                if isinstance(obj, Element):
                    # add directly as a child
                    rc.container_adders[-1].add(obj)
                    return None
        return ipython_display_formatter_original(obj)


InteractiveShell.instance().display_formatter.ipython_display_formatter = ReactonDisplayFormatter()
InteractiveShell.instance().display_pub.publish = publish
