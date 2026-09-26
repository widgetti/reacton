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


# ---- the mount (reacton.core._RenderContextFast): contexts and the render context are plain
# Python objects (the update paths use them from Python), elements are typed

cdef class _Mount:
    cdef public object rc
    cdef public list recording
    cdef public list contexts
    cdef public list order
    cdef public bint failed
    cdef public Py_ssize_t raised
    cdef public set shared_next
    cdef public dict keys
    cdef public list adders
    cdef public ContainerAdder body_adder
    cdef public object top


cdef int _plain_class(object cls) except -1
cdef object _trait_names(object component)

@cython.locals(m=_Mount, c=object, widget=object)
cpdef object mount_component(object rc, ElementBase el, object key, object parent_context, object order, object context)

cdef object _new_context(object parent)
cdef object _adopt(object precreated, object parent)

@cython.locals(rc=object, precreated_children=object, nodes=list, managers=object, raised=Py_ssize_t, provides=Py_ssize_t, root=object, widget=object, adders=list, user_contexts=object)
cdef object _mount_component(_Mount m, ElementBase el, object parent, list parent_nodes, object context, object key)

@cython.locals(root=object)
cdef object _call_body(_Mount m, ElementBase el, object managers)

@cython.locals(component=object, default_container=object, adder=ContainerAdder, created=list, container_adders=list, root_element=object, kwargs=dict)
cdef object _call_component(_Mount m, ElementBase el)

@cython.locals(key=object, all_keys=dict, keys=set, component=object, precreated=object, precreated_children=object, child=object, widget=object, kwargs=dict, resolved=dict, name=object, value=object, new_value=object, rc=object, element_class=object, plain=int, callback_wrappers=dict, listener=object, recording=list, count=Py_ssize_t, listeners=dict, traits=frozenset, callback=object, widget_class=object, handlers=tuple, handler=object, orphan_ids=object, widgets_dict=object)
cdef object _mount_node(_Mount m, ElementBase el, object c, list nodes, object dkey)

@cython.locals(values=list, index=Py_ssize_t, x=object, w=object)
cdef list _mount_list(_Mount m, object value, object c, list nodes, object dkey)

cdef object _mount_value(_Mount m, object value, object c, list nodes, object dkey)

@cython.locals(order=list, raised=bint, context=object, effects=object, parent=object, effect=object, widget=object, el=ElementBase, key=object)
cpdef object finish_mount(object rc, object root)

@cython.locals(nodes=list, w=_Materialize, root=object)
cpdef object materialize(object c)

cdef class _Materialize:
    cdef public bint partial
    cdef public list nodes
    cdef public Py_ssize_t index
    cdef public Py_ssize_t order
    cdef public dict elements
    cdef public dict widgets
    cdef public dict children
    cdef public dict element_to_widget
    cdef public set used_keys
    cdef public dict resolved_kwargs

    @cython.locals(key=object, component=object, child=object, widget=object, resolved=dict, start=Py_ssize_t, name=object, value=object, new_value=object, node=object, traits=frozenset)
    cpdef object node(self, ElementBase el, object default_key)

    @cython.locals(t=object, values=list, index=Py_ssize_t, x=object, w=object)
    cpdef object value(self, object value, object key)


@cython.locals(el=object, widget=object, orphans=object, orphan=object, orphan_widget=object, close=object)
cdef object _close_widget_node(object rc, object node, object widgets_dict)

@cython.locals(context=object, widgets_dict=object, effect=object, cleanup=object, handler=object, nodes=list, node=object)
cpdef object remove_mounted(object rc, object child_context, bint closing)


# ---- the hooks

cdef class RefBase:
    cdef dict __dict__
    cdef object __weakref__
    cdef public object current


cdef class _EventHandler:
    cdef public object rc, context, callback, event, widget, registered_event
    cdef public bint removed


@cython.locals(rc=object, context=object, index=Py_ssize_t, state=dict, value=object, setters=dict, setter=object, eq_cell=list)
cpdef use_state(initial, key=*, eq=*)

@cython.locals(rc=object)
cpdef use_ref(initial_value)

@cython.locals(memo=object, index=Py_ssize_t, value=object, dependencies_previous=object)
cdef object _use_ref(object context, object initial_value)

@cython.locals(rc=object, context=object, name=object, memo=object, index=Py_ssize_t, value=object, entry=tuple, dependencies_previous=object)
cpdef use_memo(f, dependencies=*, debug_name=*)

@cython.locals(rc=object, context=object, effects=object, index=Py_ssize_t, previous_effect=object)
cpdef use_effect(effect, dependencies=*)

@cython.locals(vue=object)
cdef object _is_vue(object component)

@cython.locals(rc=object, context=object, ref=object, handler=object, component=object, events=object, handlers=tuple)
cpdef use_event(el, event_and_modifiers, callback)


cdef class _Listener:
    cdef public object rc, context, name, widget, callback


cdef class _Setter:
    cdef public object rc, context, key
    cdef public list _reacton_eq
    cdef public object created_stack
