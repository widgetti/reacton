import logging
import os
import re
from inspect import isclass
from textwrap import indent
from typing import List, Type

import black
import bqplot
import ipywidgets
import ipywidgets as widgets  # type: ignore
import numpy as np
import traitlets  # type: ignore
import traittypes
from jinja2 import Template

import react_ipywidgets as react
from react_ipywidgets.core import Element

from . import logging as _logging  # type: ignore # noqa: F401

MAX_LINE_LENGTH = 160 - 8
logger = logging.getLogger("react")

type_name_alias = {"ipyvue.Template.Template": "ipyvue.Template", "ipywidgets.widgets.widget.Widget": "ipywidgets.Widget"}
typemap = {
    traitlets.traitlets.CaselessStrEnum: "str",
    traitlets.traitlets.Enum: "str",
    traittypes.traittypes.Array: "ndarray",
    ipywidgets.widgets.trait_types.TypedTuple: "Tuple",
    traitlets.traitlets.CInt: "int",
    traitlets.traitlets.Int: "int",
    traitlets.traitlets.Unicode: "str",
    traitlets.traitlets.CUnicode: "str",
    traitlets.traitlets.Bool: "bool",
    traitlets.traitlets.Bytes: "bytes",
    traitlets.traitlets.CFloat: "float",
    traitlets.traitlets.Float: "float",
    ipywidgets.widgets.trait_types.Date: "datetime.date",
    ipywidgets.widgets.trait_types.Color: "str",
    traitlets.traitlets.Any: "Any",
    ipywidgets.widgets.trait_types.NumberFormat: "str",
    bqplot.traits.Date: "datetime.datetime",
    tuple: "tuple",
    # ipywidgets.widgets.widget.Widget: "widgets.Widget",z
    list: "List",
    dict: "Dict",
}


default_alias = {bqplot.Map.map_data: "bqplot.Map.map_data.default"}


def fix_class_name(class_name):
    if class_name.startswith("ipyvuetify"):
        parts = class_name.split(".")
        if parts[-1] == parts[-2]:
            parts = parts[:-2] + [parts[-1]]
        class_name = ".".join(parts)
    return class_name


def inject_components(module, g):
    for cls_name in dir(module):
        cls = getattr(module, cls_name)
        if isclass(cls) and issubclass(cls, widgets.Widget):
            g[cls_name] = react.component(cls)


class repr_wrap:
    def __init__(self, repr):
        self.repr = repr

    def __repr__(self):
        return self.repr


def generate_component(cls: Type[widgets.Widget], ignore_traits: List[str] = [], extra_arguments=[], blacken=True, element_class=react.core.Element):
    docstring_args_template = Template(
        """
{% for arg in docargs %}
:param {{ arg.name }}: {{ arg.help }}{% endfor %}
"""
    )

    template_method = Template(
        """

def {{ method_name }}({{ signature }}) -> Element[{{class_name}}]:
    \"\"\"{{class_docstring}}
    {{docstring_args}}
    \"\"\"
    kwargs : Dict[Any, Any] = without_default({{ method_name }}, locals())
    {{InstanceDict_fixes}}
    widget_cls = {{class_name}}
    comp = react.core.ComponentWidget(widget=widget_cls)
    return {{element_class_name}}(comp, **kwargs)
    """
    )
    element_class_name = element_class.__name__
    ignore = "comm log keys".split() + ignore_traits
    traits = {key: value for key, value in cls.class_traits().items() if "output" not in value.metadata and not key.startswith("_") and key not in ignore}

    def has_default(trait):
        default = trait.default()
        if isinstance(default, np.ndarray):
            return True
        return default != traitlets.Undefined

    def get_default(trait):
        if trait in default_alias:
            return repr_wrap(default_alias[trait])
        if isinstance(trait, ipywidgets.widgets.trait_types.InstanceDict):
            assert trait.default_args is None
            assert trait.default_kwargs is None
            return {}
        if isinstance(trait, ipywidgets.widgets.trait_types.TypedTuple):
            if len(trait.default_args) == 0:
                return tuple()
            else:
                assert len(trait.default_args) == 1
                return trait.default_args[0]
        if isinstance(trait, traitlets.traitlets.Tuple):
            return trait.make_dynamic_default()
        if isinstance(trait, traitlets.traitlets.List):
            return trait.make_dynamic_default()
        if isinstance(trait, traitlets.traitlets.Dict):
            return trait.make_dynamic_default()
        if isinstance(trait, traittypes.traittypes.Array):
            value = trait.make_dynamic_default()
            if value is not None:
                value = value.tolist()
                value = repr_wrap(f"np.array({value!r})")
            return value
        if hasattr(trait, "make_dynamic_default"):
            if trait.default_args is None and trait.default_kwargs is None:
                return None
            else:
                raise ValueError(
                    f"Cannot have default value for dynamic default, {trait} should have an instance of"
                    "{trait.klass} with args {trait.default_args} and {trait.default_kwargs}"
                )
        return trait.default()

    types = {}

    def get_type(trait):
        if isinstance(trait, ipywidgets.widgets.trait_types.TypedTuple):
            sub = get_type(trait._trait)
            return f"Sequence[{sub}]"
        if isinstance(trait, ipywidgets.widgets.trait_types.InstanceDict):
            type_name = str(trait.klass.__module__) + "." + trait.klass.__name__
            type_name = type_name_alias.get(type_name, type_name)
            if issubclass(trait.klass, widgets.Widget):
                type_name = f"Element[{type_name}]"
            return f"Union[Dict[str, Any], {type_name}]"
        if isinstance(trait, traitlets.traitlets.Union):
            if len(trait.trait_types) == 1:
                return get_type(trait.trait_types[0])
            subs = ", ".join([get_type(t) for t in trait.trait_types])
            return f"typing.Union[{subs}]"
        # if isinstance(trait, traitlets.traitlets.Tuple):
        # TODO: we can special case this (Tuple is subclass of Instance)
        # but it's fixed length
        if isinstance(trait, traitlets.traitlets.Instance):
            if trait.klass.__name__ == "array":
                import pdb

                pdb.set_trace()
            if trait.klass.__module__ == "builtins":
                return trait.klass.__name__
            else:
                type_name = str(trait.klass.__module__) + "." + trait.klass.__name__
                type_name = type_name_alias.get(type_name, type_name)
                if issubclass(trait.klass, widgets.Widget):
                    type_name = f"{element_class_name}[{type_name}]"
                return type_name

        return typemap[type(trait)]

    InstanceDict_fixes_list = []
    for name, trait in traits.items():
        if isinstance(trait, ipywidgets.widgets.trait_types.InstanceDict):
            component = trait.klass.__name__
            if trait.klass.__module__ == "ipywidgets.widgets.widget_layout":
                if cls.__module__.startswith("ipywidgets"):
                    component = "Layout"
                else:
                    component = "w.Layout"
            InstanceDict_fixes_list.append(f"if isinstance(kwargs.get('{name}'), dict): kwargs['{name}'] = {component}(**kwargs['{name}'])")

        try:
            types[name] = get_type(trait)
            if types[name] == "array":
                import pdb

                pdb.set_trace()
        except Exception:
            logging.exception("Cannot find type for trait %r of %r", name, cls)
            raise
    InstanceDict_fixes = indent("\n".join(InstanceDict_fixes_list), "    ").strip()

    # from ipyvue.Template import Template as t

    traits_nodefault = {key: value for key, value in traits.items() if not has_default(value)}
    traits_default = {key: value for key, value in traits.items() if key not in traits_nodefault}
    signature_list = ["{name}".format(name=name) for name, value in traits_nodefault.items()]
    signature_list.extend([f"{name}: {types[name]} ={get_default(value)!r}" for name, value in traits_default.items()])
    args_list = ["{name}={name}".format(name=name) for name, value in traits.items()]
    for name, trait in traits.items():
        typing_type = get_type(trait)
        callback_type = f"typing.Callable[[{typing_type}], Any]"
        signature_list.append(f"on_{name}: {callback_type}=None")
        args_list.append(f"on_{name}=on_{name}")
    for name, default, arg_type in extra_arguments:
        signature_list.append(f"{name}: {arg_type}={default!r}")
    args = ", ".join(args_list)
    signature = ", ".join(signature_list)

    signature_list = ["{name}={value!r}".format(name=name, value=value.default_value) for name, value in traits.items()]
    full_signature = ", ".join(signature_list)
    full_args = args

    method_name = cls.__name__
    module = cls.__module__
    class_name = module + "." + cls.__name__
    class_name = fix_class_name(class_name)
    # class_docstring = "\n".join(wrap(cls.__doc__ or "", MAX_LINE_LENGTH))
    class_docstring = cls.__doc__ or ""

    doctraits = {name: trait for name, trait in traits.items() if "help" in trait.metadata}
    docargs = [{"name": name, "help": trait.metadata["help"]} for name, trait in doctraits.items()]

    kwargs = dict(locals())
    docstring_args = docstring_args_template.render(**kwargs)
    docstring_args = indent(docstring_args, "    ").strip()

    kwargs = dict(locals())
    code = template_method.render(**kwargs)
    if blacken:
        mode = black.Mode(line_length=MAX_LINE_LENGTH)
        try:
            code = black.format_file_contents(code, fast=False, mode=mode)
        except Exception:
            print("code:\n", code)
            raise
    return code


def camel_to_underscore(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def find_widget_classes(module):
    for cls_name in dir(module):
        cls = getattr(module, cls_name)
        if isclass(cls) and issubclass(cls, widgets.Widget):
            yield cls


def generate(path, modules, ignore_traits=[], blacken=True, module_output=None):
    code_snippets = []
    found = set()
    for module in modules:
        for cls in find_widget_classes(module):
            if cls not in found:
                found.add(cls)
                if cls != widgets.Widget:
                    extra_arguments = getattr(module_output, "extra_arguments", {}).get(cls, [])
                    element_class = getattr(module_output, "element_classes", {}).get(cls, Element)
                    code = generate_component(cls, ignore_traits=ignore_traits, blacken=blacken, extra_arguments=extra_arguments, element_class=element_class)
                    code_snippets.append(code)
    code = ("\n###\n").join(code_snippets)
    with open(path) as f:
        current_code = f.read()
    marker = "# generated code:"
    start = current_code.find(marker)
    if start == -1:
        raise ValueError(f"Could not find marker: {marker!r}")
    start = current_code.find("\n", start)
    if start == -1:
        raise ValueError(f"Could not find new line after marker: {marker!r}")
    code_total = current_code[: start + 1] + code
    if blacken:
        import black

        mode = black.Mode(line_length=MAX_LINE_LENGTH)
        code_total = black.format_file_contents(code_total, fast=False, mode=mode)
    only_valid = True
    if only_valid:
        try:
            exec(code_total)
        except Exception as exception:
            print(code_total)
            logger.exception("Did not generate correct code")
            print(exception)
            return
    with open(path, "w") as f:
        print(code_total, file=f)
    os.system(f"mypy {path}")
    # print(code)
