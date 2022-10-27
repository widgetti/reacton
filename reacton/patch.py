import traitlets


class Callable(traitlets.traitlets.TraitType):
    info_text = "a callable"

    def validate(self, obj, value):
        if callable(value):
            return value
        else:
            self.error(obj, value)


# for py36 we are stuck with a version that does not have this
if not hasattr(traitlets.traitlets, "Callable"):
    traitlets.traitlets.Callable = Callable
    traitlets.Callable = Callable

if not hasattr(traitlets.traitlets.TraitType, "default"):

    def default(self, obj=None):
        """The default generator for this trait
        Notes
        -----
        This method is registered to HasTraits classes during ``class_init``
        in the same way that dynamic defaults defined by ``@default`` are.
        """
        if self.default_value is not traitlets.traitlets.Undefined:
            return self.default_value
        elif hasattr(self, "make_dynamic_default"):
            return self.make_dynamic_default()  # type:ignore[attr-defined]
        else:
            # Undefined will raise in TraitType.get
            return self.default_value

    traitlets.traitlets.TraitType.default = default
