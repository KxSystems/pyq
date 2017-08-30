#if PY_MAJOR_VERSION < 3
#define DEFERRED_ADDRESS(ADDR) 0

static void
mv_dup_buffer(Py_buffer *dest, Py_buffer *src)
{
    *dest = *src;
    if (src->ndim == 1 && src->shape != NULL) {
        dest->shape = &(dest->smalltable[0]);
        dest->shape[0] = src->shape[0];
    }
    if (src->ndim == 1 && src->strides != NULL) {
        dest->strides = &(dest->smalltable[1]);
        dest->strides[0] = src->strides[0];
    }
}

static int
mv_getbuffer(PyMemoryViewObject *self, Py_buffer *view, int flags)
{
    int res;
    KObject *obj = (KObject *) PyMemoryView_GET_BASE(self);
    res = _k_getbuffer(obj, view, flags, 1);
    if (view)
        mv_dup_buffer(view, &self->view);
    return res;
}

static PyBufferProcs mv_as_buffer = {
    (readbufferproc) 0,
    (writebufferproc) 0,
    (segcountproc) 0,
    (charbufferproc) 0,
    (getbufferproc) mv_getbuffer,
    (releasebufferproc) 0,
};

static PyTypeObject MemoryView_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "pyq._k._MemoryView",
    sizeof(PyMemoryViewObject),
    0,
    0,                                        /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    PyObject_GenericGetAttr,                  /* tp_getattro */
    0,                                        /* tp_setattro */
    &mv_as_buffer,                            /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_NEWBUFFER, /* tp_flags */
    0,                                        /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    0,                                        /* tp_methods */
    0,                                        /* tp_members */
    0,                                        /* tp_getset */
    DEFERRED_ADDRESS(&PyMemoryView_Type),     /* tp_base */
};
#define INIT_MV \
    MemoryView_Type.ob_type = &PyType_Type;       \
    MemoryView_Type.tp_base = &PyMemoryView_Type; \
    PyType_Ready(&MemoryView_Type)
static PyObject *
MemoryView_FromBuffer(Py_buffer *view)
{
    PyObject *mv;
#ifdef COUNT_ALLOCS
    PyTypeObject *tmp;
#endif
    mv = PyMemoryView_FromBuffer(view);
#ifdef COUNT_ALLOCS
    tmp = mv->ob_type;
#endif
    mv->ob_type = &MemoryView_Type;
    Py_INCREF(mv->ob_type);
#ifdef COUNT_ALLOCS
    Py_DECREF(tmp);
#endif
    return mv;
}
#define PyMemoryView_FromBuffer MemoryView_FromBuffer
#else
#define INIT_MV
#endif
