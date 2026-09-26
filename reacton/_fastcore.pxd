# Cython declarations for _fastcore.py (pure Python mode). Everything that makes the compiled
# module fast is declared here, so the .py runs as plain Python without paying for it.
cimport cython


cdef class ContainerAdder:
    cdef dict __dict__
    cdef object __weakref__
    cdef public object el, prop_name
    cdef public list created


cdef class ElementBase:
    cdef dict __dict__
    cdef object __weakref__
    cdef public object component
    cdef public object args
    cdef public object kwargs
    cdef public object mime_bundle
    cdef public object _key
    cdef public object _meta
    cdef public object _on_kwargs
    cdef public object _leaf
    cdef public object _event_handlers
    cdef public bint is_shared
    cdef public Py_ssize_t _render_count


cdef class ValueElementBase(ElementBase):
    cdef public object value_property
