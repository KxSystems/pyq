/* -*- mode: c; c-basic-offset: 4 -*- */
static char __version__[] = "$Revision: 10002$";
#define KX36 (10*KXVER + KXVER2 >= 36)
/*
  K object layout (KXVER < 3, 32 bit):
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
+-------+---+---+-------+--------
|   r   | t | u |   n   |  G0 ...
+-------+---+---+-+-----+--------
                |g|
                +-+-+
                | h |
                +---+---+
                |   i   |
                +-------+-------+
                |       j       |
                +-------+ ------+
                |   e   |
                +-------+-------+
                |       f       |
                +---+---+-------+
                |   s   |
                +-------+
                |   k   |
                +-------+

  K object layout (KXVER >= 3, 64 bit):
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
+-+-+-+-+-------+---------------+--------
|m|a|t|u|   r   |       n       |  G0 ...
+-+-+-+-+-------+-+-------------+--------
                |g|
                +-+-+
                | h |
                +---+---+
                |   i   |
                +-------+-------+
                |       j       |
                +-------+ ------+
                |   e   |
                +-------+-------+
                |       f       |
                +---------------+
                |       s       |
                +-------+-------+
                |       k       |
                +---------------+
*/
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "datetime.h"
#include "longintrepr.h"

#include "kx/k.h"

#include <float.h>
#include <stddef.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>
#include <math.h>
#if defined(WIN32) || defined(_WIN32)
#    ifndef isnan
#        define isnan _isnan
#    endif
#    ifndef isfinite
#        define isfinite _finite
#    endif
double
round(double d)
{
    return floor(d + 0.5);
}
#endif


#    define PY_SET_SN(var, obj)                              \
        {                                                    \
            Py_ssize_t size;                                 \
            char const *str = PyUnicode_AsUTF8AndSize(obj, &size); \
            var = sn((S)str, (I)size);                          \
        }

#define HAVE_EE (KXVER >= 3 && KXVER2 >= 5)

#if HAVE_EE
K ee(K);
#endif /* have ee() */

ZK
km(I i)
{
    K x = ka(-KM);

    xi = i;
    R x;
}

ZK
kuu(I i)
{
    K x = ka(-KU);

    xi = i;
    R x;
}

ZK
kv(I i)
{
    K x = ka(-KV);

    xi = i;
    R x;
}

typedef struct {
    PyObject_HEAD K x;
} KObject;

static PyTypeObject K_Type;

#define K_Check(op) PyObject_TypeCheck(op, &K_Type)
#define K_CheckExact(op) (Py_TYPE(op) == &K_Type)

PyDoc_STRVAR(
    module_doc,
    "Low level q interface module.\n"
    "\n"
    "Provides a K object - python handle to q datatypes.\n"
    "\n"
    "This module is implemented as a thin layer on top of C API, k.h.  Most\n"
    "functions described in http://kx.com/q/c/c.txt are\n"
    "implemented as methods of the K class.  Names of the functions are "
    "formed by\n"
    "prefixing the names with an _.  Note that this module\n"
    "is not intended for the end user, but rather as a building block for\n"
    "the higher level q module.\n"
    "\n"
    "Summary of q datatypes\n"
    "----------------------\n"
    "type: KB KG KH KI KJ KE KF KC KS KD KT KZ 0(nested list)\n"
    "code:  1  4  5  6  7  8  9 10 11 14 19 15\n"
    ">>> KB,KG,KH,KI,KJ,KE,KF,KC,KS,KD,KT,KZ\n"
    "(1, 4, 5, 6, 7, 8, 9, 10, 11, 14, 19, 15)\n"
    "\n"
    "t| size literal      q         c                \n"
    "------------------------------------------------\n"
    "b  1    0b           boolean   unsigned char    \n"
    "x  1    0x0          byte      unsigned char    \n"
    "h  2    0h           short     short            \n"
    "i  4    0            int       int              \n"
    "j  8    0j           long      long long        \n"
    "e  4    0e           real      float            \n"
    "f  8    0.0          float     double           \n"
    "c  1    "
    "          char      unsigned char    \n"
    "s  .    `            symbol    unsigned char*   \n"
    "p  8    dateDtime    timestamp long long        \n"
    "m  4    2000.01m     month     int              \n"
    "d  4    2000.01.01   date      int              \n"
    "z  8    dateTtime    datetime  double           \n"
    "n  8    1D02:03      timespan  long long        \n"
    "u  4    00:00        minute    int              \n"
    "v  4    00:00:00     second    int              \n"
    "t  4    00:00:00.000 time      int              \n"
    "*  4    `s$`         enum                       \n");

#define ENUMS_END 77
Z I debug;
/* K objects */
ZK k_none;
ZK k_nil;
ZK k_noargs;

static PyObject *ErrorObject;

/* always consumes x reference */
static PyObject *
KObject_FromK(PyTypeObject *type, K x)
{
    KObject *self;

    if (!type)
        type = &K_Type;
    if (x == NULL) {
        PyErr_SetString(PyExc_SystemError,
                        "attempted to create null K object");
        R NULL;
    }
    if (xt == -128) {
        PyErr_SetString(ErrorObject, xs ? xs : (S) "not set");
        R r0(x), NULL;
    }
    self = (KObject *)type->tp_alloc(type, 0);
    if (self)
        self->x = x;
    else
        r0(x);

    return (PyObject *)self;
}

/* converter function */
static int
getK(PyObject *arg, void *addr)
{
    K r;
    if (!K_Check(arg)) {
        return PyErr_BadArgument();
    }
    r = ((KObject *)arg)->x;

    /*
       if (!r) {
       return PyErr_BadArgument();
       }
     */
    *(K *)addr = r;
    return 1;
}

static void
K_dealloc(KObject *self)
{
    if (self->x) {
        r0(self->x);
    }
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
K_dot(KObject *self, KObject *args)
{
    if (K_Check(args)) {
        K x;
        Py_BEGIN_ALLOW_THREADS
#if HAVE_EE
            x = dot(self->x, args->x);
            if (!x)
                x = ee(x);
#else
            x = k(0, ".", r1(self->x), r1(args->x), (K)0);
#endif /* have ee() */
        Py_END_ALLOW_THREADS
        return KObject_FromK(Py_TYPE(self), x);
    }
    return PyErr_Format(PyExc_TypeError,
                        "expected a K object, not %.200s",
                        Py_TYPE(args)->tp_name);
}

ZK get_backtrace_dl;
Z K2(get_backtrace)
{
    K r = ka(-127);
    r->k = knk(2, r1(x), r1(y));
    R r;
}

static PyObject *
K_trp(KObject *self, KObject *args)
{
    if (K_Check(args)) {
        K x = knk(3, r1(self->x), r1(args->x), r1(get_backtrace_dl));
        Py_BEGIN_ALLOW_THREADS
            x = k(0, "-105!", x, (K)0);
        Py_END_ALLOW_THREADS
        if (xt != -127) {
            return KObject_FromK(Py_TYPE(self), x);
        }
        else {
            K x0, x1;
            PyObject *exc_value, *message, *traceback;
            x0 = kK(xk)[0];
            x1 = kK(xk)[1];
            message = PyUnicode_FromStringAndSize((S)kG(x0), (Py_ssize_t)x0->n);
            traceback = KObject_FromK(Py_TYPE(self), r1(x1));
            r0(x);
            exc_value = PyObject_CallFunctionObjArgs(
                ErrorObject, message, traceback, NULL);
            Py_DECREF(message);
            Py_DECREF(traceback);
            PyErr_SetObject(ErrorObject, exc_value);
            return NULL;
        }
    }
    return PyErr_Format(PyExc_TypeError,
                        "expected a K object, not %.200s",
                        Py_TYPE(args)->tp_name);
}

/* extern K a1(K,K); */
static PyObject *
K_a0(KObject *self)
{
    K x = self->x;
    if (xt < 100) {
        Py_INCREF(self);
        return (PyObject *)self;
    }
    Py_BEGIN_ALLOW_THREADS
#if HAVE_EE
        x = dot(x, k_noargs);
        if (!x)
            x = ee(x);
#else
        x = k(0, "@", r1(x), r1(k_none), (K)0);
#endif /* have ee() */
    Py_END_ALLOW_THREADS
    return KObject_FromK(Py_TYPE(self), x);
}

static PyObject *
K_a1(KObject *self, KObject *arg)
{
    if (K_Check(arg)) {
        K x, y;
        Py_BEGIN_ALLOW_THREADS
#if HAVE_EE
            y = knk(1, r1(arg->x));
            x = dot(self->x, y);
            r0(y);
            if (!x)
                x = ee(x);
#else
            y = arg->x;
            x = k(0, "@", r1(self->x), r1(y), (K)0);
#endif /* have ee() */
        Py_END_ALLOW_THREADS
        return KObject_FromK(Py_TYPE(self), x);
    }
    return PyErr_Format(PyExc_TypeError,
                        "expected a K object, not %.200s",
                        Py_TYPE(arg)->tp_name);
}

static PyObject *
K_ja(KObject *self, PyObject *arg)
{
    switch (self->x->t) {
    case 0: {
        if (K_Check(arg))
            jk(&self->x, r1(((KObject *)arg)->x));
        else
            R PyErr_Format(PyExc_TypeError,
                           "K._ja: expected K object, not %s",
                           Py_TYPE(arg)->tp_name);
        break;
    }
    case KB: {
        if (PyBool_Check(arg)) {
            G a = (arg == Py_True);

            ja(&self->x, &a);
        }
        else
            R PyErr_Format(PyExc_TypeError,
                           "K._ja: expected bool, not %s",
                           Py_TYPE(arg)->tp_name);
        break;
    }
    case KG: {
        G g;
        long a = PyLong_AsLong(arg);

        if (a == -1 && PyErr_Occurred())
            R NULL;
        if (a < 0 || a > 257) {
            PyErr_Format(PyExc_OverflowError,
                         "Expected an integer between 0 and 257, not %ld",
                         a);
            R NULL;
        }
        g = (G)a;
        ja(&self->x, &g);
        break;
    }
    case KH: {
        H h;
        long a = PyLong_AsLong(arg);
        if (a == -1 && PyErr_Occurred()) {
            if (arg == Py_None) {
                PyErr_Clear();
                h = nh;
            }
            else
                R NULL;
        }
        else {
            h = (H)(a < -wh ? -wh : (a > wh ? wh : a));
        }
        ja(&self->x, &h);
        break;
    }
    case KI: {
        I i;
        long long a = PyLong_AsLongLong(arg);
        if (a == -1 && PyErr_Occurred()) {
            if (arg == Py_None) {
                PyErr_Clear();
                i = ni;
            }
            else
                R NULL;
        }
        else {
            i = (I)(a < -wi ? -wi : (a > wi ? wi : a));
        }
        ja(&self->x, &i);
        break;
    }
    case KJ: {
        int overflow;
        J j = PyLong_AsLongLongAndOverflow(arg, &overflow);
        if (j == -1 && PyErr_Occurred()) {
            if (arg == Py_None) {
                PyErr_Clear();
                j = nj;
            }
            else
                R NULL;
        }
        if (overflow) {
            j = overflow * wj;
        }
        ja(&self->x, &j);
        break;
    }
    case KE: {
        E e;
        double a = PyFloat_AsDouble(arg);
        if (a == -1 && PyErr_Occurred()) {
            if (arg == Py_None) {
                PyErr_Clear();
                e = (E)nf;
            }
            else {
                R NULL;
            }
        }
        else {
            e = (E)(a <= -FLT_MAX ? -wf : a >= FLT_MAX ? wf : a);
        }
        ja(&self->x, &e);
        break;
    }
    case KF: {
        F a = PyFloat_AsDouble(arg);

        if (a == -1 && PyErr_Occurred()) {
            if (arg == Py_None) {
                PyErr_Clear();
                a = nf;
            }
            else {
                R NULL;
            }
        }
        ja(&self->x, &a);
        break;
    }
    case KC: {
        char *a;

        Py_ssize_t n;

        if (-1 == PyBytes_AsStringAndSize(arg, &a, &n))
            R NULL;

        if (n != 1)
            R PyErr_Format(
                PyExc_TypeError, "K.ja: a one-, not %zd-character string", n);
        ja(&self->x, a);
        break;
    }
    case KS: {
        char *a;
        Py_ssize_t n;
        if (-1 == PyBytes_AsStringAndSize(arg, &a, &n))
            R NULL;
        /* TODO: check for overflow in the cast to (I). */
        js(&self->x, sn(a, (I)n));
        break;
    }
    case KM: {
    }
    case KD: {
    }
    case KZ: {
    }
    case KU: {
    }
    case KV: {
    }
    case KT: {
    }
    default:
        R PyErr_Format(PyExc_NotImplementedError,
                       "appending to type %d",
                       (int)self->x->t);
    }
    Py_RETURN_NONE;
}

static PyObject *
K_jv(KObject *self, KObject *arg)
{
    if (!K_Check(arg))
        R PyErr_Format(PyExc_TypeError,
                       "K._jv: expected K object, not %s",
                       Py_TYPE(arg)->tp_name);
    jv(&self->x, arg->x);
    Py_RETURN_NONE;
}

static K k_repr;

static PyObject *
K_str(KObject *self)
{
    PyObject *res;
    K x = self->x;

    switch (xt) {
    case KC:
        return PyUnicode_FromStringAndSize((S)xC, (Py_ssize_t)xn);
    case -KS:
        return PyUnicode_InternFromString(xs);
    case -KC:
        return PyUnicode_FromStringAndSize((S)&xg, 1);
    case 101:
        if (xj == 0)
            return PyUnicode_FromString("::");
    }
    if (-xt >= 20 && -xt < ENUMS_END) {
        x = k(0, "value", r1(x), (K)0);
        if (xt == -128)
            return PyErr_SetString(ErrorObject, xs ? xs : (S) "not set"),
                   r0(x), NULL;
        if (xt == -11) {
            res = PyUnicode_InternFromString(xs);
            r0(x);
            return res;
        }
        /* Pass through - deleted enum vector */
    }
    x = k(0, "@", r1(k_repr), r1(x), (K)0);
    if (xt == -128)
        return PyErr_SetString(ErrorObject, xs ? xs : (S) "not set"), r0(x),
               NULL;
    res = PyUnicode_FromStringAndSize((S)xC, (Py_ssize_t)xn);
    r0(x);
    return res;
}

static PyObject *
K_repr(KObject *self)
{
    K x = self->x;

    PyObject *f, *s, *r;

    /* special-case :: (issue #663) */
    if (xt == 101 && xj == 0)
        R PyUnicode_FromString("k('::')");

    x = k(0, "@", r1(k_repr), r1(x), (K)0);
    if (xt == -128) {
        r = PyUnicode_FromFormat(
            "<k object at %p of type %hd, '%s>", self->x, (H)self->xt, xs);
        R r0(x), r;
    }

    f = PyUnicode_FromString("k(%r)");
    if (f == NULL)
        R r0(x), NULL;

    s = PyUnicode_FromStringAndSize((S)xC, (Py_ssize_t)xn);
    if (s == NULL) {
        Py_DECREF(f);
        R r0(x), NULL;
    }

    r = PyUnicode_Format(f, s);
    Py_DECREF(f);
    Py_DECREF(s);
    R r0(x), r;
}

/** Array interface **/

/* Array Interface flags */
#define CONTIGUOUS 0x001
#define FORTRAN 0x002
#define ALIGNED 0x100
#define NOTSWAPPED 0x200
#define WRITEABLE 0x400
#define ARR_HAS_DESCR 0x800

typedef struct {
    int version;
    int nd;
    char typekind;
    int itemsize;
    int flags;
    Py_intptr_t *shape;
    Py_intptr_t *strides;
    void *data;
    PyObject *descr;
} PyArrayInterface;

/*                           01234567890123456789  */
static char typechars[20] = "ObXXuiiiffSOiiifiiii";

static int
k_typekind(K x)
{
    unsigned int t = abs(xt);

    if (t < sizeof(typechars))
        return typechars[t];
    if (t < ENUMS_END)
        return 'i';
    return 'X';
}

static int
k_itemsize(K x)
{
    static int itemsizes[] = {
        sizeof(void *),
        1, /* bool */
#if KXVER >= 3
        16,
#else
        0,
#endif
        0,
        1,              /* byte */
        2,              /* short */
        4,              /* int */
        8,              /* long */
        4,              /* float */
        8,              /* real */
        1,              /* char */
        sizeof(void *), /* symbol */
        8,              /* timestamp */
        4,              /* month */
        4,              /* date */
        8,              /* datetime */
        8,              /* timespan */
        4,              /* minute */
        4,              /* second */
        4,              /* time */
#if KX36
        8,              /* 64bit enum */
#endif
    };
    unsigned int t = abs(xt);

    if (t < sizeof(itemsizes) / sizeof(*itemsizes))
        return itemsizes[t];
    if (t < ENUMS_END)
        return 4;
    return 0;
}

static void
k_array_struct_free(PyObject *cap)
{
    void *ptr = PyCapsule_GetPointer(cap, NULL);
    void *arr = PyCapsule_GetContext(cap);

    PyArrayInterface *inter = (PyArrayInterface *)ptr;
    if (inter->shape != NULL)
        free(inter->shape);
    free(inter);
    Py_DECREF((PyObject *)arr);
}

static PyObject *
K_array_struct_get(KObject *self)
{
    K x = self->x;
    PyArrayInterface *inter;
    int typekind, nd;
    typekind = k_typekind(x);

    if (abs(xt) >= KS || xt == 0) {
        PyErr_Format(PyExc_AttributeError, "k object of type %dh", xt);
        return NULL;
    }

    if (!(inter = (PyArrayInterface *)malloc(sizeof(PyArrayInterface))))
        goto fail_inter;
    nd = (xt >= 0); /* scalars have t < 0 in k4 */

    inter->version = 2;
    inter->nd = nd;
    inter->typekind = typekind;
    inter->itemsize = k_itemsize(x);
    inter->flags = ALIGNED | NOTSWAPPED | WRITEABLE | CONTIGUOUS;
    if (nd) {
        if (!(inter->shape = (Py_intptr_t *)malloc(sizeof(Py_intptr_t) * 2)))
            goto fail_shape;
        inter->shape[0] = (Py_ssize_t)xn;
        inter->strides = inter->shape + 1;
        inter->strides[0] = inter->itemsize;
        inter->data = kG(x);
    }
    else {
        inter->shape = inter->strides = NULL;
        inter->data = &xg;
    }
    Py_INCREF(self);
    PyObject *cap = PyCapsule_New(inter, NULL, &k_array_struct_free);
    if (PyCapsule_SetContext(cap, self)) {
        Py_DECREF(cap);
        return NULL;
    }
    return cap;
fail_shape:
    free(inter);
fail_inter:
    return PyErr_NoMemory();
}

static PyObject *
K_array_typestr_get(KObject *self)
{
    K x = self->x;

    static int const one = 1;

    char const endian = "><"[(int)*(char const *)&one];

    char const typekind = k_typekind(x);

    return PyUnicode_FromFormat(
        "%c%c%d", typekind == 'O' ? '|' : endian, typekind, k_itemsize(x));
}

static PyObject *K_K(PyTypeObject *type, PyObject *arg);

static int
arg_names(K f, S *names, Py_ssize_t *pn)
{
    K x;
    switch (f->t) {
    case 100:
        x = kK(f)[1];
        *pn = (Py_ssize_t)xn;
        DO(xn, names[i] = xS[i]);
        break;
    case 101:
        *pn = 1;
        names[0] = "x";
        break;
    case 102:
        *pn = 2;
        names[0] = "x";
        names[1] = "y";
        break;
    case 103:
    case 104:
    case 106:
        x = k(0, ".pyq.an", r1(f), (K)0);
        *pn = (Py_ssize_t)xn;
        DO(xn, names[i] = xS[i]);
        r0(x);
        break;
    default:
        PyErr_Format(PyExc_TypeError,
                     "K object of type %d cannot be called with kwds",
                     (int)f->t);
        return -1;
    }
    return 0;
}

static PyObject *
call_args(K f, PyObject *args, PyObject *kwds)
/* Return a tuple of arguments extracted from args and kwds.
   Compare to inspect.getcallargs.
 */
{
    PyObject *ret, *a;
    Py_ssize_t i, n, m;
    S names[8];

    if (arg_names(f, names, &m) == -1)
        return NULL;
    n = PyTuple_GET_SIZE(args);
    if (n > m) {
        PyErr_Format(PyExc_TypeError, "too many positional arguments");
        return NULL;
    }
    if (kwds == NULL) {
        Py_INCREF(args);
        return args;
    }
    ret = PyTuple_New(m);
    if (ret == NULL)
        return NULL;
    for (i = 0; i < n; ++i) {
        a = PyTuple_GET_ITEM(args, i);
        Py_INCREF(a);
        PyTuple_SET_ITEM(ret, i, a);
        /* check that positional arguments are not duplicated in kwds */
        a = PyDict_GetItemString(kwds, names[i]);
        if (a != NULL) {
            Py_DECREF(ret);
            ret = PyErr_Format(
                PyExc_TypeError, "duplicate value for argument %s", names[i]);
            goto done;
        }
    }
    n = PyDict_Size(kwds);
    for (; i < m; ++i) {
        a = PyDict_GetItemString(kwds, names[i]);
        if (a == NULL)
            a = KObject_FromK(&K_Type, r1(k_nil));
        else
            n--; /* track the count of remaining kwds */
        Py_INCREF(
            a); /* NB: PyDict_GetItemString returns a borrowed reference */
        PyTuple_SET_ITEM(ret, i, a);
    }
    if (n > 0) {
        PyErr_Format(PyExc_TypeError, "unexpected keyword argument");
        Py_DECREF(ret);
        ret = NULL;
    }
done:
    return ret;
}

static PyObject *
K_callargs(KObject *self, PyObject *args, PyObject *kwds)
{
    return call_args(self->x, args, kwds);
}

static PyObject *
K_call(KObject *self, PyObject *args, PyObject *kwds)
{
    PyTypeObject *type = Py_TYPE(self);
    PyObject *ret = NULL, *kargs;
    Py_ssize_t i, n;
    if (self->xt >= 100 && kwds != NULL && PyDict_Size(kwds) > 0) {
        args = call_args(self->x, args, kwds);
        if (args == NULL)
            return NULL;
    }
    else
        Py_INCREF(args);

    switch ((n = PyTuple_GET_SIZE(args))) {
    case 0:
        Py_DECREF(args);
        R K_a0(self);
    case 1: {
        PyObject *a = PyTuple_GET_ITEM(args, 0);
        if (!K_Check(a)) {
            a = PyObject_CallFunctionObjArgs((PyObject *)type, a, NULL);
            if (a == NULL) {
                Py_DECREF(args);
                return NULL;
            }
        }
        else
            Py_INCREF(a);
        ret = K_a1(self, (KObject *)a);
        Py_DECREF(a);
        Py_DECREF(args);
        return ret;
    }
    }
    /* TODO: Unpack arguments directly to K list */
    for (i = 0; i < n; ++i) {
        PyObject *old_arg, *new_arg;
        old_arg = PyTuple_GET_ITEM(args, i);
        if (!K_Check(old_arg)) {
            new_arg =
                PyObject_CallFunctionObjArgs((PyObject *)type, old_arg, NULL);
            if (new_arg == NULL) {
                Py_DECREF(args);
                return NULL;
            }
            PyTuple_SET_ITEM(args, i, new_arg);
            Py_DECREF(old_arg);
        }
    }
    kargs = K_K(type, args);
    if (kargs == NULL) {
        Py_DECREF(args);
        R NULL;
    }
    ret = K_dot(self, (KObject *)kargs);
    Py_DECREF(kargs);
    Py_DECREF(args);
    R ret;
}

static PyObject *
array_descr(PyObject *obj)
{
    PyObject *tmp;

    tmp = PyObject_GetAttrString(obj, "dtype");
    if (tmp == NULL)
        return NULL;
    obj = tmp;
    tmp = PyObject_GetAttrString(obj, "str");
    Py_DECREF(obj);

    return tmp;
}

static int
k_ktype(PyArrayInterface *inter, PyObject *obj, J *offset, J *scale)
{
    int typekind = inter->typekind;
    int itemsize = inter->itemsize;
    switch (typekind) {
    case 'f':
        switch (itemsize) {
        case 4:
            return KE;
        case 8:
            return KF;
        default:
            goto error;
        }
    case 'i':
        switch (itemsize) {
        case 1:
            return KG;
        case 2:
            return KH;
        case 4:
            return KI;
        case 8:
            return KJ;
        default:
            goto error;
        }
    case 'S':
        if (itemsize == 1)
            return KC;
        else
            goto error;
    case 'b':
        return KB;
    case 'O':
        return KS;
    case 'u':
        if (itemsize == 1)
            return KG;
        else
            goto error;
    case 'M': {
        char const *s;
        char unit, unit2;
        Py_ssize_t n;
        PyObject *descr = array_descr(obj);
        if (descr == NULL)
            return -1;
        if ((s = PyUnicode_AsUTF8AndSize(descr, &n)) == NULL) {
            Py_DECREF(descr);
            return -1;
        }
        if (n < 5 || itemsize != 8) {
            PyErr_Format(PyExc_TypeError, "invalid descr %s", s);
            Py_DECREF(descr);
            return -1;
        }
        unit = s[4];
        unit2 = s[5];
        Py_DECREF(descr);
        switch (unit) {
        case 'Y':
            *offset = (1970 - 2000) * 12;
            *scale = 12;
            return KM;
        case 'M':
            *offset = (1970 - 2000) * 12;
            *scale = 1;
            return KM;
        case 'W':
            *offset = -10957;
            *scale = 7;
            return KD;
        case 'D':
            *offset = -10957;
            *scale = 1;
            return KD;
        case 'h': /* hour */
            *offset = -10957 * 24 * 60 * 60 * 1000000000LL;
            *scale = 60 * 60 * 1000000000LL;
            return KP;          /* timestamp */
        case 'm':               /* minute or millisecond */
            if (unit2 == 's') { /* millisecond */
                *offset = -10957 * 24 * 60 * 60 * 1000000000LL;
                *scale = 1000000LL;
            }
            else { /* minute */
                *offset = -10957 * 24 * 60 * 60 * 1000000000LL;
                *scale = 60 * 1000000000LL;
            }
            return KP; /* timestamp */
        case 's':      /* second */
            *offset = -10957 * 24 * 60 * 60 * 1000000000LL;
            *scale = 1000000000LL;
            return KP; /* timestamp */
        case 'u':      /* microsecond */
            *offset = -10957 * 24 * 60 * 60 * 1000000000LL;
            *scale = 1000LL;
            return KP; /* timestamp */
        case 'n':      /* nanosecond */
            *offset = -10957 * 24 * 60 * 60 * 1000000000LL;
            *scale = 1;
            return KP; /* timestamp */

        default:
            PyErr_Format(PyExc_TypeError, "invalid descr %s", s);
            return -1;
        }
    }
    case 'm': {
        char const *s;
        char unit[2];
        Py_ssize_t n;
        PyObject *descr = array_descr(obj);
        if (descr == NULL)
            return -1;
        if ((s = PyUnicode_AsUTF8AndSize(descr, &n)) == NULL) {
            Py_DECREF(descr);
            return -1;
        }
        if (n < 5) {
            PyErr_Format(PyExc_TypeError, "invalid descr %s", s);
            Py_DECREF(descr);
            return -1;
        }
        unit[0] = s[n - 2];
        unit[1] = s[n - 3];
        Py_DECREF(descr);
        switch (unit[0]) {
        case 's':
            switch (unit[1]) {
            case 'n':
                *scale = 1LL;
                break;
            case 'u':
                *scale = 1000LL;
                break;
            case 'm':
                *scale = 1000000LL;
                break;
            case '[':
                *scale = 1000000000LL;
                break;
            default:
                PyErr_Format(PyExc_TypeError, "invalid descr %s", s);
                return -1;
            }
            break;
        case 'm':
            *scale = 60 * 1000000000LL;
            break;
        case 'h':
            *scale = 60 * 60 * 1000000000LL;
            break;
        case 'D':
            *scale = 24 * 60 * 60 * 1000000000LL;
            break;
        case 'W':
            *scale = 7 * 24 * 60 * 60 * 1000000000LL;
            break;
        default:
            PyErr_Format(PyExc_TypeError, "invalid descr %s", s);
            return -1;
        }
        return KN;
    }
    case 'V': {
        PyErr_SetString(PyExc_NotImplementedError,
                        "typecode 'V' is not implemented in C");
        return -1;
    }
    }
error:
    PyErr_Format(PyExc_TypeError,
                 "cannot handle type '%c%d'",
                 inter->typekind,
                 inter->itemsize);
    return -1;
}

ZC k_types[128];
ZK _from_memoryview(PyTypeObject *type, PyObject *arg);
ZK _from_array_struct(PyTypeObject *type, PyObject *arg);

/* K class methods */

PyDoc_STRVAR(K_from_memoryview_doc, "K object from memoryview");
static PyObject *
K_from_memoryview(PyTypeObject *type, PyObject *arg)
{
    K x = _from_memoryview(type, arg);
    if (x)
        return KObject_FromK(type, x);
    else
        return NULL;
}

ZK
_from_memoryview(PyTypeObject *type, PyObject *arg)
{
    K x = NULL;
    Py_buffer view;
    if (PyObject_GetBuffer(arg, &view, PyBUF_ND|PyBUF_FORMAT) != -1) {
        I t;
        if (strlen(view.format) != 1 || (t = k_types[(int)*view.format]) == 0) {
            PyErr_Format(PyExc_NotImplementedError, "NYI format=%s", view.format);
            goto done;
        }
        switch (view.ndim) {
            case 0:
                x = ka(-t);
                memcpy(&xg, view.buf, view.itemsize);
            break;
            case 1:
                x = ktn(t, view.shape[0]);
                memcpy(xG, view.buf, view.len);
            break;
            default:
                PyErr_Format(PyExc_NotImplementedError, "NYI ndim=%d", (I)view.ndim);
                goto done;
        }
    }
    else {
        return NULL;
    }
  done:
    PyBuffer_Release(&view);
    R x;
}

PyDoc_STRVAR(K_from_array_struct_doc, "K object from __array_struct__");
static PyObject *
K_from_array_struct(PyTypeObject *type, PyObject *arg)
{
    K x = _from_array_struct(type, arg);
    if (x)
        return KObject_FromK(type, x);
    else
        return NULL;
}

static int
c_contiguous(PyArrayInterface *inter)
{
    if ((inter->flags & CONTIGUOUS) || inter->strides == NULL)
        return 1;
    else {
        int r = 1, n = inter->nd, i;
        Py_intptr_t stride = inter->itemsize;
        for (i = n - 1; i >= 0; --i) {
            r &= (inter->strides[i] == stride);
            stride *= inter->shape[i];
        }
        return r;
    }
}

ZK
_from_array_struct(PyTypeObject *type, PyObject *arg)
{
    PyArrayInterface *inter;
    PyObject *obj;
    J offset = 0, scale = 1, size = 1;
    K x, shape = (K)0;
    int t, itemsize;

    if (!PyCapsule_CheckExact(arg)) {
        PyErr_Format(PyExc_ValueError,
                     "invalid __array_struct__ type:"
                     " expected PyCapsule, not %.200s",
                     Py_TYPE(arg)->tp_name);
        return NULL;
    }
    inter = (PyArrayInterface *)PyCapsule_GetPointer(arg, NULL);
    if (inter == NULL)
        return NULL;
    obj = (PyObject *)PyCapsule_GetContext(arg);
    if (obj == NULL)
        return NULL;

    if (inter->version != 2) {
        PyErr_Format(PyExc_ValueError,
                     "invalid __array_struct__:"
                     " expected version 2, not %d",
                     inter->version);
        return NULL;
    }
    t = k_ktype(inter, obj, &offset, &scale);
    if (t < 0) {
        return NULL;
    }
    if (inter->nd > 1) {
        if (t > KC) {
            PyErr_Format(PyExc_ValueError,
                         "Cannot handle nd=%d, kind='%c'",
                         inter->nd,
                         inter->typekind);
            return NULL;
        }

        shape = ktn(KJ, inter->nd);
        if (shape == (K)0) {
            PyErr_NoMemory();
            return NULL;
        }
        DO(inter->nd, kJ(shape)[i] = inter->shape[i]);
        DO(inter->nd, size *= inter->shape[i]);
    }
    else if (inter->nd == 1)
        size = inter->shape[0];
    /* if nd == 0 - size = 1 */
    itemsize = inter->itemsize;
    x = inter->nd ? ktn(t, size) : ka(-t);
    if (!x) {
        PyErr_NoMemory();
        R NULL;
    }
    if (xt == -128) {
        PyErr_SetString(ErrorObject, xs);
        return NULL;
    }
    if (t == KS) {
        PyObject **src = (PyObject **)inter->data;

        if (inter->nd) {
            S *dest = xS;

            Py_intptr_t n = inter->shape[0], i;

            dest = xS;
            for (i = 0; i < n; ++i) {
                PyObject *obj = src[i * inter->strides[0] / itemsize];

                if (!PyUnicode_Check(obj)) {
                    PyErr_SetString(PyExc_ValueError,
                                    "non-string in object array");
                    r0(x);
                    return NULL;
                }
                PY_SET_SN(dest[i], obj)
            }
        }
        else {
            PyObject *obj = src[0];

            PY_SET_SN(xs, obj)
        }
    }
    else if (t == KD || t == KM) {
        if (inter->nd) {
            DO(inter->shape[0],
               xI[i] = (I)(offset +
                           scale * *(long long *)((S)inter->data +
                                                  i * inter->strides[0])));
        }
        else
            xi = (I)(offset + scale * *(long long *)inter->data);
    }
    else if (t == KP) {
        if (inter->nd) {
            DO(inter->shape[0],
               xJ[i] = offset + scale * *(long long *)((S)inter->data +
                                                       i * inter->strides[0]));
        }
        else
            xj = offset + scale * *(long long *)inter->data;
    }
    else if (t == KN && scale != 1) {
        if (inter->nd) {
            DO(inter->shape[0],
               xJ[i] = (J)(scale * *(long long *)((S)inter->data +
                                                  i * inter->strides[0])));
        }
        else
            xj = (J)(scale * *(long long *)inter->data);
    }
    else {
        void *dest = (xt < 0) ? &xg : xG;
        if (c_contiguous(inter)) {
            memcpy(dest, inter->data, (size_t)(size * itemsize));
        }
        else {
            if (inter->nd == 1) {
                Py_intptr_t n = inter->shape[0];
                DO(n,
                   memcpy(xG + i * itemsize,
                          (S)inter->data + i * inter->strides[0],
                          itemsize));
            }
            else {
                r0(x);
                r0(shape);
                PyErr_Format(PyExc_ValueError, "strided nd=%d", inter->nd);
                return NULL;
            }
        }
    }
    if (shape) {
        x = k(0, "#", shape, x, (K)0);
    }
    return x;
}

PyDoc_STRVAR(K_ktd_doc, "flip from keyed table(dict)");
static PyObject *
K_ktd(PyTypeObject *type, PyObject *args)
{
    K x = 0;

    if (!PyArg_ParseTuple(args, "O&", &getK, &x)) {
        return NULL;
    }
    assert(x);
    /*
       Note that if the ktd conversion fails for any reason,
       it returns 0 and x is not freed.
       since 2011-01-27, ktd always decrements ref count of input.
       <http://code.kx.com/q/interfaces/c-client-for-q/#creating-dictionaries-and-tables>
    */
#if HAVE_EE
    return KObject_FromK(type, ee(ktd(r1(x))));
#else
    return KObject_FromK(type, k(0, "0!", r1(x), (K)0));
#endif /* have ee() */
}

PyDoc_STRVAR(K_err_doc, "sets a K error\n\n>>> K.err('test')\n");
static PyObject *
K_err(PyTypeObject *type, PyObject *args)
{
    S s;

    if (!PyArg_ParseTuple(args, "s:err", &s)) {
        return NULL;
    }
    krr(s);
    Py_RETURN_NONE;
}

#define NFD 1024
Z PyObject *cb[NFD];
Z K
di(I d)
{
    PyObject *r;
    PyGILState_STATE gstate = PyGILState_Ensure();
    r = PyObject_CallFunction(cb[d], "i", d);
    if (r == NULL) {
        if (debug)
            PyErr_Print();
        else
            PyErr_Clear();
        /* remove offending callback on error */
        sd0(d);
        Py_DECREF(cb[d]);
        cb[d] = NULL;
        PyGILState_Release(gstate);
        R krr("py");
    }
    Py_DECREF(r);
    PyGILState_Release(gstate);
    R 0;
}

PyDoc_STRVAR(K_sd0_doc, "stop");
static PyObject *
K_sd0(PyTypeObject *type, PyObject *args)
{
    I d;
    if (!PyArg_ParseTuple(args, "i:sd0", &d)) {
        return NULL;
    }
    if (d < 0 || d >= NFD || cb[d] == NULL) {
        PyErr_Format(PyExc_ValueError, "bad descriptor - %d", d);
        return NULL;
    }
    sd0(d);
    Py_DECREF(cb[d]);
    cb[d] = NULL;
    Py_RETURN_NONE;
}

PyDoc_STRVAR(K_sd1_doc, "start");
static PyObject *
K_sd1(PyTypeObject *type, PyObject *args)
{
    I d;
    PyObject *f;
    K x;

    if (!PyArg_ParseTuple(args, "iO:sd1", &d, &f)) {
        return NULL;
    }
    if (d < 0 || d >= NFD || cb[d] != NULL) {
        PyErr_Format(PyExc_ValueError, "bad descriptor - %d", d);
        return NULL;
    }
    Py_INCREF(f);
    cb[d] = f;
    x = sd1(d, di);

    return PyLong_FromLong(xi);
}

PyDoc_STRVAR(K_ka_doc, "returns a K atom");
static PyObject *
K_ka(PyTypeObject *type, PyObject *args)
{
    H t;
    J j;
    K x;

    if (!PyArg_ParseTuple(args, "hL:K._ka", &t, &j))
        return NULL;
    x = ktj(t, j);

    return KObject_FromK(type, x);
}

#define K_ATOM(a, T, t, doc)                                   \
    PyDoc_STRVAR(K_k##a##_doc, doc);                           \
    static PyObject *K_k##a(PyTypeObject *type, PyObject *arg) \
    {                                                          \
        K x;                                                   \
        T g;                                                   \
        if (py2##a(arg, &g) == -1)                             \
            return NULL;                                       \
        x = k##a(g);                                           \
        return KObject_FromK(type, x);                         \
    }

static int
py2j(PyObject *obj, J *j)
{
    PY_LONG_LONG val;
    int overflow;
    PyObject *int_obj = PyNumber_Index(obj);
    if (int_obj == NULL)
        return -1;

    if (PyLong_Check(int_obj)) {
        val = PyLong_AsLongLongAndOverflow(int_obj, &overflow);
        Py_DECREF(int_obj);
        if (val == -1 && PyErr_Occurred())
            return -1;
        if (val == nj)
            overflow = -1;
        if (overflow) {
            /* Return +- inf on overflow */
            val = overflow * wj;
        }
    }
    else {
        Py_DECREF(int_obj);
        PyErr_Format(PyExc_TypeError, "__index__ returned a non-integer");
        return -1;
    }
    *j = val;
    return 0;
}

static int
py2b(PyObject *obj, G *g)
{
    if (obj == Py_True)
        *g = 1;
    else if (obj == Py_False || obj == Py_None)
        *g = 0;
    else {
        J x;
        if (py2j(obj, &x) == -1)
            return -1;
        *g = (G)(x != 0);
    }
    return 0;
}

static int
py2i(PyObject *obj, I *i)
{
    J j;
    if (py2j(obj, &j) == -1)
        return -1;
    if (j <= -wi) {
        *i = -wi;
    }
    else if (j >= wi) {
        *i = wi;
    }
    else
        *i = (I)j;

    return 0;
}

static int
py2h(PyObject *obj, H *h)
{
    J j;
    if (py2j(obj, &j) == -1)
        return -1;
    if (j <= -wh) {
        *h = -wh;
    }
    else if (j >= wh) {
        *h = wh;
    }
    else
        *h = (H)j;

    return 0;
}

static int
py2g(PyObject *obj, G *g)
{
    J j;
    if (py2j(obj, &j) == -1)
        return -1;

    if (j > 0xff || j < 0) {
        PyErr_Format(PyExc_OverflowError, "too big");
        return -1;
    }
    *g = (G)j;
    return 0;
}

static int
py2c(PyObject *obj, C *c)
{
    if (PyUnicode_Check(obj)) {
        obj = PyUnicode_AsUTF8String(obj);
        if (obj == NULL)
            return -1;
    }
    else if (PyBytes_Check(obj)) {
        Py_INCREF(obj);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "expected bytes or str, not %.200s.",
                     Py_TYPE(obj)->tp_name);
        return -1;
    }

    if (PyBytes_GET_SIZE(obj) != 1) {
        PyErr_Format(PyExc_TypeError, "expected char, not str");
        Py_DECREF(obj);
        return -1;
    }
    *c = *PyBytes_AS_STRING(obj);
    Py_DECREF(obj);
    return 0;
}

static int
py2f(PyObject *obj, F *f)
{
    PyObject *float_obj;
    float_obj = PyNumber_Float(obj);
    if (float_obj == NULL)
        return -1;
    *f = PyFloat_AS_DOUBLE(float_obj);
    Py_DECREF(float_obj);
    return 0;
}

static int
py2e(PyObject *obj, E *e)
{
    F f;
    if (py2f(obj, &f) == -1)
        return -1;
    *e = (E)f;
    return 0;
}

#define MAX_P 106285 /* = ymd(2290, 12, 31) */
#define MIN_P -MAX_P /* = ymd(1709, 1, 1) */
#define NS_IN_DAY 24 * 60 * 60 * 1000000000LL
/* timestamp/span or +/- 0Wj if strict - 0Nj and set error */
ZJ
clip_p(I ord, J n)
{
    int overflow = 0;
    if (ord > MAX_P)
        overflow = 1;
    else if (ord < MIN_P)
        overflow = -1;

    if (overflow)
        return overflow * wj;

    return (J)ord * NS_IN_DAY + n;
}

static int
py2p(PyObject *obj, J *j)
{
    J p, n = 0;
    I ord;
    if (py2j(obj, &p) == -1) {
        PyErr_Clear();
        if (!PyDate_Check(obj)) {
            PyErr_Format(PyExc_TypeError, "expected int or date");
            return -1;
        }
        ord = ymd(PyDateTime_GET_YEAR(obj),
                  PyDateTime_GET_MONTH(obj),
                  PyDateTime_GET_DAY(obj));
        if (PyDateTime_Check(obj)) {
            int h, m, s, u;
            h = PyDateTime_DATE_GET_HOUR(obj);
            m = PyDateTime_DATE_GET_MINUTE(obj);
            s = PyDateTime_DATE_GET_SECOND(obj);
            u = PyDateTime_DATE_GET_MICROSECOND(obj);
            n = (((h * 60 + m) * 60 + s) * 1000000LL + u) * 1000LL;
        }
        p = clip_p(ord, n);
    }
    *j = p;
    return 0;
}

static int
py2z(PyObject *obj, F *f)
{
    if (PyFloat_Check(obj)) {
        *f = PyFloat_AS_DOUBLE(obj);
    }
    else {
        J p;
        if (py2p(obj, &p) == -1)
            return -1;
        *f = p / (F)NS_IN_DAY;
    }
    return 0;
}

#if KX36
#define MAX_D 2921939 /* = ymd(9999, 12, 31) */
#define MIN_D -730119 /* = ymd(1, 1, 1) */
#define MAX_M 95999   /* "i"$9999.12m */
#define MIN_M -23988  /* "i"$0001.01m */
#else
#define MAX_D 106285 /* = ymd(2290, 12, 31) */
#define MIN_D -MAX_P /* = ymd(1709, 1, 1) */
#define MAX_M 3491         /* "i"$2290.12m */
#define MIN_M (-MAX_M - 1) /* "i"$1709.01m */
#endif

static int
py2m(PyObject *obj, I *i)
{
    I month;
    int overflow = 0;
    if (py2i(obj, &month) == -1) {
        PyErr_Clear();
        if (PyDate_Check(obj)) {
            int y, m;
            y = PyDateTime_GET_YEAR(obj);
            m = PyDateTime_GET_MONTH(obj);
            month = 12 * (y - 2000) + m - 1;
#if KX36  /* With kdb+ version >= 3.6, month range matches that of Python dates. */
            goto done;
#endif
        }
        else {
            PyErr_Format(PyExc_TypeError, "expected int or date");
            return -1;
        }
    }
    if (month > MAX_M)
        overflow = 1;
    else if (month < MIN_M)
        overflow = -1;
    if (overflow)
        month = overflow * wi;
#if KX36
done:
#endif
    *i = month;
    return 0;
}

static int
py2d(PyObject *obj, I *i)
{
    I date;
    int overflow = 0;
    if (py2i(obj, &date) == -1) {
        PyErr_Clear();
        if (PyDate_Check(obj)) {
            int y, m, d;
            y = PyDateTime_GET_YEAR(obj);
            m = PyDateTime_GET_MONTH(obj);
            d = PyDateTime_GET_DAY(obj);
            date = ymd(y, m, d);
#if KX36  /* With kdb+ version >= 3.6, month range matches that of Python dates. */
            goto done;
#endif
        }
        else {
            PyErr_Format(PyExc_TypeError, "expected int or date");
            return -1;
        }
    }
    if (date > MAX_D)
        overflow = 1;
    else if (date < MIN_D)
        overflow = -1;
    if (overflow)
        date = overflow * wi;
#if KX36
done:
#endif
    *i = date;
    return 0;
}

static int
py2n(PyObject *obj, J *j)
{
    J n, m = 0;
    if (py2j(obj, &n) == -1) {
        int d, s, u;
        PyErr_Clear();
        if (!PyDelta_Check(obj)) {
            PyErr_Format(PyExc_TypeError, "expected int or timedelta");
            return -1;
        }
        d = ((PyDateTime_Delta *)obj)->days;
        s = ((PyDateTime_Delta *)obj)->seconds;
        u = ((PyDateTime_Delta *)obj)->microseconds;
        m = (s * 1000000LL + u) * 1000LL;
        n = clip_p(d, m);
    }
    *j = n;
    return 0;
}

#define MAX_U 5999     /* "i"$99:59  */
#define MIN_U (-MAX_U) /* "i"$-99:59 */

static int
py2u(PyObject *obj, I *i)
{
    I minute;
    int overflow = 0;
    if (py2i(obj, &minute) == -1) {
        PyErr_Clear();
        if (PyTime_Check(obj)) {
            int h, m;
            h = PyDateTime_TIME_GET_HOUR(obj);
            m = PyDateTime_TIME_GET_MINUTE(obj);
            minute = h * 60 + m;
        }
        else {
            PyErr_Format(PyExc_TypeError, "expected int or time");
            return -1;
        }
    }
    if (minute > MAX_U)
        overflow = 1;
    else if (minute < MIN_U)
        overflow = -1;
    if (overflow)
        minute = overflow * wi;
    *i = minute;
    return 0;
}

#define MAX_V 599999   /* "i"$99:59:59  */
#define MIN_V (-MAX_U) /* "i"$-99:59:59 */

static int
py2v(PyObject *obj, I *i)
{
    I second;
    int overflow = 0;
    if (py2i(obj, &second) == -1) {
        PyErr_Clear();
        if (PyTime_Check(obj)) {
            int h, m, s;
            h = PyDateTime_TIME_GET_HOUR(obj);
            m = PyDateTime_TIME_GET_MINUTE(obj);
            s = PyDateTime_TIME_GET_SECOND(obj);
            second = (h * 60 + m) * 60 + s;
        }
        else {
            PyErr_Format(PyExc_TypeError, "expected int or time");
            return -1;
        }
    }
    if (second > MAX_V)
        overflow = 1;
    else if (second < MIN_V)
        overflow = -1;
    if (overflow)
        second = overflow * wi;
    *i = second;
    return 0;
}

#define MAX_T 359999999 /* "i"$99:59:59.999  */
#define MIN_T (-MAX_T)  /* "i"$-99:59:59.999  */

static int
py2t(PyObject *obj, I *i)
{
    I time;
    int overflow = 0;
    if (py2i(obj, &time) == -1) {
        PyErr_Clear();
        if (PyTime_Check(obj)) {
            int h, m, s, u;
            h = PyDateTime_TIME_GET_HOUR(obj);
            m = PyDateTime_TIME_GET_MINUTE(obj);
            s = PyDateTime_TIME_GET_SECOND(obj);
            u = PyDateTime_TIME_GET_MICROSECOND(obj);
            time = 1000 * ((h * 60 + m) * 60 + s) + u / 1000;
        }
        else {
            PyErr_Format(PyExc_TypeError, "expected int or time");
            return -1;
        }
    }
    if (time > MAX_T)
        overflow = 1;
    else if (time < MIN_T)
        overflow = -1;
    if (overflow)
        time = overflow * wi;
    *i = time;
    return 0;
}

PyDoc_STRVAR(K_B_doc, "returns a K boolean list");
static PyObject *
K_B(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;

    G item;

    PyObject *seq = PySequence_Fast(arg, "K._B: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KB, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (py2b(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xG[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_kb_doc, "converts any object to q boolean");
static PyObject *
K_kb(PyTypeObject *type, PyObject *arg)
{
    G g;
    K x;
    if (py2b(arg, &g) == -1)
        return NULL;
    x = kb(g);
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_G_doc, "returns a K byte list");
static PyObject *
K_G(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;

    G item;

    PyObject *seq = PySequence_Fast(arg, "K._G: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KG, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = 0;
        else if (py2g(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xG[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_H_doc, "returns a K short list");
static PyObject *
K_H(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;

    H item;

    PyObject *seq = PySequence_Fast(arg, "K._H: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KH, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = nh;
        else if (py2h(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xH[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_I_doc, "returns a K int list");
static PyObject *
K_I(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;

    I item;

    PyObject *seq = PySequence_Fast(arg, "K._I: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KI, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = ni;
        else if (py2i(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xI[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_J_doc, "returns a K long list");
static PyObject *
K_J(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;

    J item;

    PyObject *seq = PySequence_Fast(arg, "K._J: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KJ, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = nj;
        else if (py2j(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xJ[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

K_ATOM(g, G, b, "returns a K byte")
K_ATOM(h, H, h, "returns a K short")
K_ATOM(i, I, i, "returns a K int")
K_ATOM(j, J, L, "returns a K long (64 bits)")
K_ATOM(e, E, f, "returns a K real (32 bits)")
K_ATOM(f, F, d, "returns a K float (64 bits)")

PyDoc_STRVAR(K_E_doc, "returns a K real list");
static PyObject *
K_E(PyTypeObject *type, PyObject *arg)
{
    E item;
    PyObject *seq = PySequence_Fast(arg, "K._E: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KE, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);
        if (o == Py_None)
            item = (E)nf;
        else if (py2e(o, &item) == -1) {
            r0(x);
            Py_DECREF(seq);
            return NULL;
        }
        xE[i] = item;
    }
    Py_DECREF(seq);
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_F_doc, "returns a K float list");
static PyObject *
K_F(PyTypeObject *type, PyObject *arg)
{
    F item;
    PyObject *seq = PySequence_Fast(arg, "K._F: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KF, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);
        if (o == Py_None)
            item = nf;
        else if (py2f(o, &item) == -1) {
            r0(x);
            Py_DECREF(seq);
            return NULL;
        }
        xF[i] = item;
    }
    Py_DECREF(seq);
    return KObject_FromK(type, x);
}

K_ATOM(c, C, c, "returns a K char")

PyDoc_STRVAR(K_ks_doc, "returns a K symbol");
static PyObject *
K_ks(PyTypeObject *type, PyObject *args)
{
    KObject *ret = 0;
    S s;
    Py_ssize_t n;
    K x;

    if (!PyArg_ParseTuple(args, "s#", &s, &n, &K_Type, &ret)) {
        return NULL;
    }
    x = ks(sn(s, (I)n));

    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_P_doc, "returns a K timestamp list");
static PyObject *
K_P(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;
    J item;
    J i, n;
    K x;

    PyObject *seq = PySequence_Fast(arg, "K._P: not a sequence");

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KP, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);
        if (o == Py_None)
            item = nj;
        else if (py2p(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xJ[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_M_doc, "returns a K month list");
static PyObject *
K_M(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;
    I item;
    J i, n;
    K x;

    PyObject *seq = PySequence_Fast(arg, "K._M: not a sequence");

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KM, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = ni;
        else if (py2m(o, &item)) {
            r0(x);
            goto error;
        }
        xI[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_D_doc, "returns a K date list");
static PyObject *
K_D(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;
    I item;
    J i, n;
    K x;

    PyObject *seq = PySequence_Fast(arg, "K._D: not a sequence");

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KD, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = ni;
        else if (py2d(o, &item)) {
            r0(x);
            goto error;
        }
        xI[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_N_doc, "returns a K timespan list");
static PyObject *
K_N(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;
    J item;
    J i, n;
    K x;

    PyObject *seq = PySequence_Fast(arg, "K._D: not a sequence");

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KN, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = nj;
        else if (py2n(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xJ[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_U_doc, "returns a K minute list");
static PyObject *
K_U(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;
    I item;
    J i, n;
    K x;

    PyObject *seq = PySequence_Fast(arg, "K._U: not a sequence");

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KU, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = ni;
        else if (py2u(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xI[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_V_doc, "returns a K second list");
static PyObject *
K_V(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;
    I item;
    J i, n;
    K x;

    PyObject *seq = PySequence_Fast(arg, "K._V: not a sequence");

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KV, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = ni;
        else if (py2v(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xI[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_T_doc, "returns a K time list");
static PyObject *
K_T(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;
    I item;
    J i, n;
    K x;

    PyObject *seq = PySequence_Fast(arg, "K._T: not a sequence");

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KT, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None)
            item = ni;
        else if (py2t(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xI[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_kzz_doc, "converts datetime.datetime to q datetime");
static PyObject *
K_kzz(PyTypeObject *type, PyObject *arg)
{
    int y, m, d, h, u, s, i;
    K x;
    if (!PyDateTime_Check(arg))
        return PyErr_Format(PyExc_TypeError,
                            "expected a datetime object, not %s",
                            Py_TYPE(arg)->tp_name);

    y = PyDateTime_GET_YEAR(arg);
    m = PyDateTime_GET_MONTH(arg);
    d = PyDateTime_GET_DAY(arg);
    h = PyDateTime_DATE_GET_HOUR(arg);
    u = PyDateTime_DATE_GET_MINUTE(arg);
    s = PyDateTime_DATE_GET_SECOND(arg);
    i = PyDateTime_DATE_GET_MICROSECOND(arg);
    x = kz(ymd(y, m, d) + (((h * 60 + u) * 60 + s) * 1000 + i / 1000) /
                              (24 * 60 * 60 * 1000.));

    return KObject_FromK(type, x);
}

#ifdef KN
PyDoc_STRVAR(K_knz_doc, "converts an integer or timedelta to q timespan");
static PyObject *
K_knz(PyTypeObject *type, PyObject *arg)
{
    J n;
    K x;
    if (py2n(arg, &n) == -1)
        return NULL;
    x = ktj(-KN, n);
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_kpz_doc, "converts an integer or date to q timestamp");
static PyObject *
K_kpz(PyTypeObject *type, PyObject *arg)
{
    K x;
    J p;
    if (py2p(arg, &p) == -1)
        return NULL;
    x = ktj(-KP, p);
    return KObject_FromK(type, x);
}
#endif
PyDoc_STRVAR(K_S_doc, "returns a K symbol list");
static PyObject *
K_S(PyTypeObject *type, PyObject *arg)
{
    PyObject *seq = PySequence_Fast(arg, "K._S: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KS, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (PyUnicode_Check(o)) {
            PY_SET_SN(xS[i], o)
        }
        else if (o == Py_None) {
            xS[i] = ss("");
        }
        else {
            r0(x);
            Py_DECREF(seq);
            PyErr_Format(
                PyExc_TypeError, "K._S: item at %lld is not a string", i);
            return NULL;
        }
    }
    Py_DECREF(seq);
    return KObject_FromK(type, x);
}

K_ATOM(m, I, i, "returns a K month")
K_ATOM(d, I, i, "returns a K date")
K_ATOM(z, F, d, "returns a K datetime")
#define ku kuu
K_ATOM(u, I, i, "returns a K minute")
#undef ku
K_ATOM(v, I, i, "returns a K second")
K_ATOM(t, I, i, "returns a K time")

PyDoc_STRVAR(K_kp_doc, "returns a K string");
static PyObject *
K_kp(PyTypeObject *type, PyObject *args)
{
    KObject *ret = 0;
    S s;
    Py_ssize_t n;
    K x;

    if (!PyArg_ParseTuple(args, "s#", &s, &n, &K_Type, &ret)) {
        return NULL;
    }
    x = kpn(s, (J)n);

    return KObject_FromK(type, x);
}

#if KXVER >= 3
/* PyObject to guid: accepts (long) integers or objects with .int attr. */
static int
py2uu(PyObject *obj, U *uu)
{
    int ret = 0;
    PyObject *int_obj, *int_attr;
    int_attr = PyObject_GetAttrString(obj, "int");
    if (int_attr == NULL) {
        PyErr_Clear();
        Py_INCREF(obj);
    }
    else
        obj = int_attr;
    int_obj = PyNumber_Index(obj);
    Py_DECREF(obj);
    if (int_obj == NULL)
        return -1;
    /* XXX: Add int/long handling in Python 2.x case. */
    if (_PyLong_AsByteArray((PyLongObject *)int_obj,
                            uu->g,
                            16, /* size */
                            0,  /* little_endian */
                            0 /* is_signed */) == -1)
        ret = -1;
    Py_DECREF(int_obj);
    return ret;
}

PyDoc_STRVAR(K_kguid_doc, "returns a K guid");
static PyObject *
K_kguid(PyTypeObject *type, PyObject *arg)
{
    U u;
    if (py2uu(arg, &u) == -1)
        return NULL;
    return KObject_FromK(type, ku(u));
}

PyDoc_STRVAR(K_UU_doc, "returns a K guid list");
static PyObject *
K_UU(PyTypeObject *type, PyObject *arg)
{
    PyObject *ret = NULL;

    U item;

    PyObject *seq = PySequence_Fast(arg, "K._UU: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(UU, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_None) {
            DO(16, item.g[i] = 0);
        }
        else if (py2uu(o, &item) == -1) {
            r0(x);
            goto error;
        }
        xU[i] = item;
    }
    ret = KObject_FromK(type, x);
error:
    Py_DECREF(seq);
    return ret;
}
#endif

PyDoc_STRVAR(K_K_doc, "returns a K general list");
static PyObject *
K_K(PyTypeObject *type, PyObject *arg)
{
    PyObject *seq = PySequence_Fast(arg, "K._K: not a sequence");
    J i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(0, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (!K_Check(o)) {
            r0(x);
            Py_DECREF(seq);
            PyErr_Format(
                PyExc_TypeError, "K._K: item at %lld is not a K object", i);
            return NULL;
        }
        xK[i] = r1(((KObject *)o)->x);
    }
    Py_DECREF(seq);
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_ktn_doc, "returns a K list");
static PyObject *
K_ktn(PyTypeObject *type, PyObject *args)
{
    K x;
    I t;
#if KXVER < 3
    I n;
    if (!PyArg_ParseTuple(args, "ii:K._ktn", &t, &n)) {
#else
    J n;
    if (!PyArg_ParseTuple(args, "iL:K._ktn", &t, &n)) {
#endif
        return NULL;
    }
    x = ktn(t, n);

    return KObject_FromK(type, x);
}

#if KXVER >= 3
PyDoc_STRVAR(K_knt_doc, "returns a keyed table");
static PyObject *
K_knt(PyTypeObject *type, PyObject *args)
{
    K x;
    J n;
    if (!PyArg_ParseTuple(args, "LO&:K._ktn", &n, getK, &x)) {
        return NULL;
    }
    if (n <= 0) {
        return PyErr_Format(PyExc_ValueError, "knt(n, t) requires n > 0, not %lld", n);
    }
#if HAVE_EE
    x = ee(knt(n, r1(x)));
#else
    {
        C cmd[32];
        sprintf(cmd, "%lld!", n);
        x = k(0, cmd, r1(x), (K)0);
    }
#endif

    return KObject_FromK(type, x);
}
#endif

PyDoc_STRVAR(K_xT_doc, "table from dictionary");
static PyObject *
K_xT(PyTypeObject *type, PyObject *args)
{
    KObject *ret = 0;

    K k0, k;

    if (!PyArg_ParseTuple(args, "O&|O!", &getK, &k0, &K_Type, &ret)) {
        return NULL;
    }
    if (!k0) {
        PyErr_BadArgument();
        return NULL;
    }
    r1(k0);
    k = xT(k0);
    return KObject_FromK(type, k);
}

PyDoc_STRVAR(K_xD_doc, "returns a K dict");
static PyObject *
K_xD(PyTypeObject *type, PyObject *args)
{
    K k1 = 0, k2 = 0, x;

    if (!PyArg_ParseTuple(args, "O&O&", getK, &k1, getK, &k2)) {
        return NULL;
    }
    if (!(k1 && k2)) {
        PyErr_BadArgument();
        return NULL;
    }
    x = xD(r1(k1), r1(k2));

    assert(xt == XD);
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_knk_doc, "returns a K list");
static PyObject *
K_knk(PyTypeObject *type, PyObject *args)
{
    I n;

    K r;

    switch (PyTuple_Size(args) - 1) {
    case 0: {
        if (!PyArg_ParseTuple(args, "i", &n)) {
            return NULL;
        }
        r = knk(n);
        break;
    }
    case 1: {
        K k1;

        if (!PyArg_ParseTuple(args, "iO&", &n, getK, &k1)) {
            return NULL;
        }
        r = knk(n, r1(k1));
        break;
    }
    case 2: {
        K k1, k2;

        if (!PyArg_ParseTuple(args, "iO&O&", &n, getK, &k1, getK, &k2)) {
            return NULL;
        }
        r = knk(n, r1(k1), r1(k2));
        break;
    }
    case 3: {
        K k1, k2, k3;

        if (!PyArg_ParseTuple(
                args, "iO&O&O&", &n, getK, &k1, getK, &k2, getK, &k3)) {
            return NULL;
        }
        r = knk(n, r1(k1), r1(k2), r1(k3));
        break;
    }
    case 4: {
        K k1, k2, k3, k4;

        if (!PyArg_ParseTuple(args,
                              "iO&O&O&O&",
                              &n,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4)) {
            return NULL;
        }
        r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4));
        break;
    }
    case 5: {
        K k1, k2, k3, k4, k5;

        if (!PyArg_ParseTuple(args,
                              "iO&O&O&O&O&",
                              &n,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5)) {
            return NULL;
        }
        r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5));
        break;
    }
    case 6: {
        K k1, k2, k3, k4, k5, k6;

        if (!PyArg_ParseTuple(args,
                              "iO&O&O&O&O&O&",
                              &n,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5,
                              getK,
                              &k6)) {
            return NULL;
        }
        r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6));
        break;
    }
    case 7: {
        K k1, k2, k3, k4, k5, k6, k7;

        if (!PyArg_ParseTuple(args,
                              "iO&O&O&O&O&O&O&",
                              &n,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5,
                              getK,
                              &k6,
                              getK,
                              &k7)) {
            return NULL;
        }
        r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), r1(k7));
        break;
    }
    case 8: {
        K k1, k2, k3, k4, k5, k6, k7, k8;

        if (!PyArg_ParseTuple(args,
                              "iO&O&O&O&O&O&O&O&",
                              &n,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5,
                              getK,
                              &k6,
                              getK,
                              &k7,
                              getK,
                              &k8)) {
            return NULL;
        }
        r = knk(
            n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), r1(k7), r1(k8));
        break;
    }
    case 9: {
        K k1, k2, k3, k4, k5, k6, k7, k8, k9;

        if (!PyArg_ParseTuple(args,
                              "iO&O&O&O&O&O&O&O&O&",
                              &n,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5,
                              getK,
                              &k6,
                              getK,
                              &k7,
                              getK,
                              &k8,
                              getK,
                              &k9)) {
            return NULL;
        }
        r = knk(n,
                r1(k1),
                r1(k2),
                r1(k3),
                r1(k4),
                r1(k5),
                r1(k6),
                r1(k7),
                r1(k8),
                r1(k9));
        break;
    }
    default:
        PyErr_BadArgument();
        return NULL;
    }
    return KObject_FromK(type, r);
}

/*
r=k(c,s,x,y,z,(K)0); decrements(r0) x,y,z. eventually program must do r0(r);
 if one of the parameters is reused you must increment, e.g.

 K x=ks("trade");
 k(-c,s,r1(x),..,(K)0);
 k(-c,s,r1(x),..,(K)0);
 ..
 r0(x);
*/
PyDoc_STRVAR(K_k_doc, "k(c, m, ...) -> k object\n");
static PyObject *
K_k(PyTypeObject *type, PyObject *args)
{
    I c;

    char *m;

    K r;

    switch (PyTuple_Size(args) - 2) {
    case 0: {
        if (!PyArg_ParseTuple(args, "is", &c, &m)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c, m, (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 1: {
        K k1;

        if (!PyArg_ParseTuple(args, "isO&", &c, &m, getK, &k1)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c, m, r1(k1), (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 2: {
        K k1, k2;

        if (!PyArg_ParseTuple(args, "isO&O&", &c, &m, getK, &k1, getK, &k2)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c, m, r1(k1), r1(k2), (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 3: {
        K k1, k2, k3;

        if (!PyArg_ParseTuple(
                args, "isO&O&O&", &c, &m, getK, &k1, getK, &k2, getK, &k3)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c, m, r1(k1), r1(k2), r1(k3), (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 4: {
        K k1, k2, k3, k4;

        if (!PyArg_ParseTuple(args,
                              "isO&O&O&O&",
                              &c,
                              &m,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 5: {
        K k1, k2, k3, k4, k5;

        if (!PyArg_ParseTuple(args,
                              "isO&O&O&O&O&",
                              &c,
                              &m,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 6: {
        K k1, k2, k3, k4, k5, k6;

        if (!PyArg_ParseTuple(args,
                              "isO&O&O&O&O&O&",
                              &c,
                              &m,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5,
                              getK,
                              &k6)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 7: {
        K k1, k2, k3, k4, k5, k6, k7;

        if (!PyArg_ParseTuple(args,
                              "isO&O&O&O&O&O&O&",
                              &c,
                              &m,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5,
                              getK,
                              &k6,
                              getK,
                              &k7)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c,
                  m,
                  r1(k1),
                  r1(k2),
                  r1(k3),
                  r1(k4),
                  r1(k5),
                  r1(k6),
                  r1(k7),
                  (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 8: {
        K k1, k2, k3, k4, k5, k6, k7, k8;

        if (!PyArg_ParseTuple(args,
                              "isO&O&O&O&O&O&O&O&",
                              &c,
                              &m,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5,
                              getK,
                              &k6,
                              getK,
                              &k7,
                              getK,
                              &k8)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c,
                  m,
                  r1(k1),
                  r1(k2),
                  r1(k3),
                  r1(k4),
                  r1(k5),
                  r1(k6),
                  r1(k7),
                  r1(k8),
                  (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    case 9: {
        K k1, k2, k3, k4, k5, k6, k7, k8, k9;

        if (!PyArg_ParseTuple(args,
                              "isO&O&O&O&O&O&O&O&O&",
                              &c,
                              &m,
                              getK,
                              &k1,
                              getK,
                              &k2,
                              getK,
                              &k3,
                              getK,
                              &k4,
                              getK,
                              &k5,
                              getK,
                              &k6,
                              getK,
                              &k7,
                              getK,
                              &k8,
                              getK,
                              &k9)) {
            return NULL;
        }
        Py_BEGIN_ALLOW_THREADS
            r = k(c,
                  m,
                  r1(k1),
                  r1(k2),
                  r1(k3),
                  r1(k4),
                  r1(k5),
                  r1(k6),
                  r1(k7),
                  r1(k8),
                  r1(k9),
                  (K)0);
        Py_END_ALLOW_THREADS
        break;
    }
    default:
        PyErr_BadArgument();
        return NULL;
    }
    if (r == NULL) {
        PyErr_SetString(PyExc_OSError, "connection");
        return NULL;
    }
    /* From the "Interfacing with Kdb+ from C" cookbook:

       If the handle is <0, this is for async messaging, and the return
       value can be either 0 (network error) or non-zero (ok).
       This result should NOT be passed to r0(r). */
    if (c < 0) {
        r = r1(k_none);
    }
    return KObject_FromK(type, r);
}

PyDoc_STRVAR(K_b9_doc, "b9(I, K) -> K byte vector\n\nserialize K object");
static PyObject *
K_b9(PyTypeObject *type, PyObject *args)
{
    I i;

    K x;

    if (!PyArg_ParseTuple(args, "iO&:K._b9", &i, &getK, &x))
        return NULL;
    return KObject_FromK(type, b9(i, x));
}

PyDoc_STRVAR(K_d9_doc, "d9(K) -> K byte vector\n\ndeserialize K object");
static PyObject *
K_d9(PyTypeObject *type, PyObject *args)
{
    K x;

    if (!PyArg_ParseTuple(args, "O&:K._b9", &getK, &x))
        return NULL;
    return KObject_FromK(type, d9(x));
}

PyDoc_STRVAR(K_inspect_doc, "inspect(k, c, [, i]) -> python object");
static PyObject *
K_inspect(PyObject *self, PyObject *args)
{
    K k = ((KObject *)self)->x;
    int i = 0;
    char c;

    if (!k) {
        PyErr_SetString(PyExc_ValueError, "null k object");
        return NULL;
    }
    int u;
    if (!PyArg_ParseTuple(args, "C|i:inspect", &u, &i)) {
        PyErr_Clear();
        if (!PyArg_ParseTuple(args, "c|i:inspect", &c, &i))
            return NULL;
    }
    else
        c = (char)u;
    switch (c) {
#if KXVER >= 3
    case 'm':
        return PyLong_FromLong(k->m);
    case 'a':
        return PyLong_FromLong(k->a);
    case 'n':
        return PyLong_FromSsize_t((Py_ssize_t)k->n);
#else
    case 'n':
        return PyLong_FromLong(k->n);
#endif
    case 'r':
        return PyLong_FromLong(k->r);
    case 't':
        return PyLong_FromLong(k->t);
    case 'u':
        return PyLong_FromLong(k->u);
        /* atoms */
    case 'g':
        return PyLong_FromLong(k->g);
    case '@':
        return _PyLong_FromByteArray(k->G0, 16, 0, 0);
    case 'h':
        return PyLong_FromLong(k->h);
    case 'i':
        return PyLong_FromLong(k->i);
    case 'j':
        return PyLong_FromLongLong(k->j);
    case 'e':
        return PyFloat_FromDouble(k->e);
    case 'f':
        return PyFloat_FromDouble(k->f);
    case 's':
        return (k->t == -KS
                    ? PyUnicode_FromString((char *)k->s)
                    : k->t == KC
                          ? PyUnicode_FromStringAndSize((char *)kG(k),
                                                     (Py_ssize_t)k->n)
                          : k->t == -KC
                                ? PyUnicode_FromStringAndSize((char *)&k->g, 1)
                                : PyUnicode_FromFormat("<%p>", k->s));
    case 'c':
        return PyBytes_FromStringAndSize((char *)&k->g, 1);
    case 'k':
        return (k->t == XT ? KObject_FromK(Py_TYPE(self), r1(k->k))
                           : PyUnicode_FromFormat("<%p>", k->k));
        /* lists */
    case 'G':
        return PyLong_FromLong(kG(k)[i]);
    case 'H':
        return PyLong_FromLong(kH(k)[i]);
    case 'I':
        return PyLong_FromLong(kI(k)[i]);
    case 'J':
        return PyLong_FromLongLong(kJ(k)[i]);
    case 'E':
        return PyFloat_FromDouble(kE(k)[i]);
    case 'F':
        return PyFloat_FromDouble(kF(k)[i]);
    case 'S':
        return (k->t == KS ? PyUnicode_FromString((char *)kS(k)[i])
                           : PyUnicode_FromFormat("<%p>", kS(k)[i]));
    case 'K':
        return KObject_FromK(Py_TYPE(self), r1(kK(k)[i]));
    }
    return PyErr_Format(PyExc_KeyError, "no such field: '%c'", c);
}
ZK py2k(PyObject *);
/* Calling Python */

ZK
python_error(void)
{
    char const *err = "n/a";
    PyObject *type, *value, *traceback;
    PyErr_Fetch(&type, &value, &traceback);
    PyErr_NormalizeException(&type, &value, &traceback);
    if (PyErr_GivenExceptionMatches(value, ErrorObject)) {
        Py_ssize_t size;
        PyObject *message;
        message = PyTuple_GET_ITEM(((PyBaseExceptionObject *)value)->args, 0);
        if ((err = PyUnicode_AsUTF8AndSize(message, &size)) == NULL) {
            err = "n/a";
            PyErr_Clear();
        }
    }
    else {
        S pdot;
        err = (S)((PyTypeObject *)type)->tp_name;
        pdot = strrchr(err, '.');
        if (pdot != NULL)
            err = pdot + 1;
    }
    /* krr does not create a copy - intern err to keep it alive */
    krr(ss((S)err));
    Py_DECREF(type);
    /* The value and traceback object may be NULL even when the type object is not. */
    Py_XDECREF(value);
    Py_XDECREF(traceback);
    R NULL;
}

ZK
call_python_object(K type, K func, K x)
{
    J n;
    K *args, r;
    PyObject *v, *res = NULL;
    PyGILState_STATE gstate;

    if (type->t != -KJ || func->t != -KJ || xt < 0 || xt >= XT) {
        R krr("type error");
    }
    n = xn;
    r1(x);
    if (xt != 0) {
        x = k(0, "(::),", x, (K)0);
        args = xK + 1;
    }
    else {
        args = xK;
    }
    gstate = PyGILState_Ensure();

    v = PyTuple_New((Py_ssize_t)n);

    DO(n,
       PyTuple_SET_ITEM(
           v, i, KObject_FromK((PyTypeObject *)type->k, r1(args[i]))));
    res = PyObject_CallObject((PyObject *)func->k, v);
    Py_DECREF(v);
    r0(x);

    if (!res) {
        r = python_error();
        goto done;
    }

    if (K_Check(res)) {
        r = r1(((KObject *)res)->x);
        goto done;
    }

    r = py2k(res);
    if (!r && PyErr_Occurred()) {
        r = python_error();
        goto done;
    }
    /* try calling K() constructor on res */
    v = PyObject_CallFunctionObjArgs((PyObject *)type->k, res, NULL);
    if (!v) {
        r = python_error();
        goto done;
    }
    r = r1(((KObject *)v)->x);
    Py_DECREF(v);
done:
    Py_XDECREF(res);
    PyGILState_Release(gstate);
    return r;
}

static PyObject *
K_func(PyTypeObject *type, PyObject *func)
{
    K f = dl(call_python_object, 3);
    K kfunc = kj(0);
    K ktype = kj(0);
    K x;

    kfunc->k = (K)func;
    ktype->k = (K)type;
    x = knk(3, f, ktype, kfunc);

    xt = 104; /* projection */
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_id_doc, "x._id() -> id of k object");
static PyObject *
K_id(KObject *self)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->x);
}

PyDoc_STRVAR(K_pys_doc, "x._pys() -> python scalar");
static PyObject *K_pys(KObject *self);

PyDoc_STRVAR(K_sp_doc, "x._sp() -> is or has special value");
static PyObject *
K_sp(KObject *self)
{
    long r = 0;
    K x = self->x;
    if (x == k_nil)
        Py_RETURN_TRUE;
    if (xt == 0) {
        DO(xn, r |= (xK[i] == k_nil));
    }
    return PyBool_FromLong(r);
}

ZS ns;

PyDoc_STRVAR(K_get_null_doc, "x._get_null() -> None if x has no missing values, q.null(x) otherwise");
static PyObject *
K_get_null(KObject *self)
{
    I r = 0;
    K x = self->x;
    switch (xt) {
        case KF:
        case KZ:
            DO(xn, r|=isnan(xF[i]));
            break;
        case KB:
        case KG:
            Py_RETURN_NONE;
        case KE:
            DO(xn, r|=isnan(xE[i]));
            break;
        case KS: {
            DO(xn, r|=(xS[i]==ns));
            break;
        }
        case KI:
        case KD:
        case KT:
        case KU:
        case KV:
            DO(xn, r|=(xI[i]==ni));
            break;
        case KJ:
            DO(xn, r|=(xJ[i]==nj));
            break;
        case KH:
            DO(xn, r|=(xH[i]==nh));
            break;
        case KC:
            DO(xn, r|=(xG[i]==' '));
            break;
#if KXVER >= 3
        case UU:
            DO(xn,{J j=0;for(;j<16;++j)r|=!xU[i].g[j];});
            break;
#endif
        default:
            r = -1;
    }
    if (r == 0)
        Py_RETURN_NONE;
    x = k(0, "null", r1(x), (K)0);
    if (r == -1) {
        if (xt < 0) {
            r = xg;
        }
        else {
            r = 0;
            DO(xn,r|=xG[i]);
        }
        if (r == 0) {
            r0(x);
            Py_RETURN_NONE;
        }
    }
    return KObject_FromK(Py_TYPE(self), x);
}

static PyMethodDef K_methods[] = {
    {"_func", (PyCFunction)K_func, METH_O | METH_CLASS, "func"},
    {"_dot", (PyCFunction)K_dot, METH_O, "dot"},
    {"_trp", (PyCFunction)K_trp, METH_O, "trp"},
    {"_a0", (PyCFunction)K_a0, METH_NOARGS, "a0"},
    {"_a1", (PyCFunction)K_a1, METH_O, "a1"},
    {"_ja", (PyCFunction)K_ja, METH_O, "append atom"},
    {"_jv", (PyCFunction)K_jv, METH_O, "append vector"},
    {"_k", (PyCFunction)K_k, METH_VARARGS | METH_CLASS, K_k_doc},
    {"_knk", (PyCFunction)K_knk, METH_VARARGS | METH_CLASS, K_knk_doc},
    {"_ktd", (PyCFunction)K_ktd, METH_VARARGS | METH_CLASS, K_ktd_doc},
    {"_err", (PyCFunction)K_err, METH_VARARGS | METH_CLASS, K_err_doc},
    {"_ktj", (PyCFunction)K_ka, METH_VARARGS | METH_CLASS, K_ka_doc},
    {"_ka", (PyCFunction)K_ka, METH_VARARGS | METH_CLASS, K_ka_doc},
    {"_kb", (PyCFunction)K_kb, METH_O | METH_CLASS, K_kb_doc},
    {"_kg", (PyCFunction)K_kg, METH_O | METH_CLASS, K_kg_doc},
    {"_kh", (PyCFunction)K_kh, METH_O | METH_CLASS, K_kh_doc},
    {"_ki", (PyCFunction)K_ki, METH_O | METH_CLASS, K_ki_doc},
    {"_B", (PyCFunction)K_B, METH_O | METH_CLASS, K_B_doc},
    {"_G", (PyCFunction)K_G, METH_O | METH_CLASS, K_G_doc},
    {"_H", (PyCFunction)K_H, METH_O | METH_CLASS, K_H_doc},
    {"_I", (PyCFunction)K_I, METH_O | METH_CLASS, K_I_doc},
    {"_J", (PyCFunction)K_J, METH_O | METH_CLASS, K_J_doc},
    {"_kj", (PyCFunction)K_kj, METH_O | METH_CLASS, K_kj_doc},
    {"_ke", (PyCFunction)K_ke, METH_O | METH_CLASS, K_ke_doc},
    {"_kf", (PyCFunction)K_kf, METH_O | METH_CLASS, K_kf_doc},
    {"_E", (PyCFunction)K_E, METH_O | METH_CLASS, K_E_doc},
    {"_F", (PyCFunction)K_F, METH_O | METH_CLASS, K_F_doc},
    {"_kc", (PyCFunction)K_kc, METH_O | METH_CLASS, K_kc_doc},
    {"_ks", (PyCFunction)K_ks, METH_VARARGS | METH_CLASS, K_ks_doc},
    {"_S", (PyCFunction)K_S, METH_O | METH_CLASS, K_S_doc},
    {"_km", (PyCFunction)K_km, METH_O | METH_CLASS, K_km_doc},
    {"_kd", (PyCFunction)K_kd, METH_O | METH_CLASS, K_kd_doc},
    {"_P", (PyCFunction)K_P, METH_O | METH_CLASS, K_P_doc},
    {"_M", (PyCFunction)K_M, METH_O | METH_CLASS, K_M_doc},
    {"_D", (PyCFunction)K_D, METH_O | METH_CLASS, K_D_doc},
    {"_N", (PyCFunction)K_N, METH_O | METH_CLASS, K_N_doc},
    {"_U", (PyCFunction)K_U, METH_O | METH_CLASS, K_U_doc},
    {"_V", (PyCFunction)K_V, METH_O | METH_CLASS, K_V_doc},
    {"_T", (PyCFunction)K_T, METH_O | METH_CLASS, K_T_doc},
    {"_kz", (PyCFunction)K_kz, METH_O | METH_CLASS, K_kz_doc},
    {"_kzz", (PyCFunction)K_kzz, METH_O | METH_CLASS, K_kzz_doc},
#ifdef KN
    {"_knz", (PyCFunction)K_knz, METH_O | METH_CLASS, K_knz_doc},
    {"_kpz", (PyCFunction)K_kpz, METH_O | METH_CLASS, K_kpz_doc},
#endif
    {"_ku", (PyCFunction)K_ku, METH_O | METH_CLASS, K_ku_doc},
#if KXVER >= 3
    {"_kguid", (PyCFunction)K_kguid, METH_O | METH_CLASS, K_kguid_doc},
    {"_UU", (PyCFunction)K_UU, METH_O | METH_CLASS, K_UU_doc},
    {"_knt", (PyCFunction)K_knt, METH_VARARGS | METH_CLASS, K_knt_doc},
#endif
    {"_kv", (PyCFunction)K_kv, METH_O | METH_CLASS, K_kv_doc},
    {"_kt", (PyCFunction)K_kt, METH_O | METH_CLASS, K_kt_doc},
    {"_kp", (PyCFunction)K_kp, METH_VARARGS | METH_CLASS, K_kp_doc},
    {"_ktn", (PyCFunction)K_ktn, METH_VARARGS | METH_CLASS, K_ktn_doc},
    {"_xT", (PyCFunction)K_xT, METH_VARARGS | METH_CLASS, K_xT_doc},
    {"_xD", (PyCFunction)K_xD, METH_VARARGS | METH_CLASS, K_xD_doc},
    {"_K", (PyCFunction)K_K, METH_O | METH_CLASS, K_K_doc},
    {"_b9", (PyCFunction)K_b9, METH_VARARGS | METH_CLASS, K_b9_doc},
    {"_d9", (PyCFunction)K_d9, METH_VARARGS | METH_CLASS, K_d9_doc},

    {"_from_memoryview",
     (PyCFunction)K_from_memoryview, METH_O | METH_CLASS,
     K_from_memoryview_doc},
    {"_from_array_struct",
     (PyCFunction)K_from_array_struct, METH_O | METH_CLASS,
     K_from_array_struct_doc},

    {"inspect", (PyCFunction)K_inspect, METH_VARARGS, K_inspect_doc},
    {"_id", (PyCFunction)K_id, METH_NOARGS, K_id_doc},
    {"_pys", (PyCFunction)K_pys, METH_NOARGS, K_pys_doc},
    {"_callargs", (PyCFunction)K_callargs, METH_VARARGS | METH_KEYWORDS, NULL},
    {"_sp", (PyCFunction)K_sp, METH_NOARGS, K_sp_doc},
    {"_get_null", (PyCFunction)K_get_null, METH_NOARGS, K_get_null_doc},
    {NULL, NULL} /* sentinel */
};

#if SIZEOF_LONG == SIZEOF_INT
#    define K_INT_CODE "l"
#    define K_LONG_CODE "q"
#elif SIZEOF_LONG == SIZEOF_LONG_LONG
#    define K_INT_CODE "i"
#    define K_LONG_CODE "l"
#else
#    error "Unsupported architecture"
#endif

char *
k_format(int t)
{
    static char *fmt[] = {
        "P", "?",         "16B",       0,          "B",
        "h", K_INT_CODE,  K_LONG_CODE, "f",        "d",
        "s", "P",         K_LONG_CODE, K_INT_CODE, K_INT_CODE,
        "d", K_LONG_CODE, K_INT_CODE,  K_INT_CODE, K_INT_CODE,
#if KX36
        K_LONG_CODE,
#else
        K_INT_CODE,
#endif
    };
    if (t <= 20)
        return fmt[t];
    if (t < 97)
        return K_INT_CODE;

    return NULL;
}

#    define _N_IS_SHAPE                                       \
        ((KXVER >= 3 && SIZEOF_VOID_P == SIZEOF_LONG_LONG) || \
         (KXVER < 3 && SIZEOF_VOID_P == SIZEOF_INT))

int
_k_getbuffer(KObject *self, Py_buffer *view, int flags, int raw)
{
    K x = self->x;
    int itemsize;
    int t = abs(xt);

    if (!raw && (t >= KS || t == 0)) {
        PyErr_Format(PyExc_BufferError, "k object of type %dh", xt);
        return -1;
    }
    itemsize = k_itemsize(x);
    /* The value of itemsize cannot be 0 here.  If raw=0, t is checked to
       be within [0, KS] in the previous if-statement.  If raw=1, k_typekind(x)
       has already been checked in K_get_data(). */
    assert(itemsize > 0);

    if (xt > 0) {
        view->ndim = 1;
        view->itemsize = itemsize;
        view->format = (flags & PyBUF_FORMAT) ? k_format(xt) : NULL;
        view->len = itemsize * (Py_ssize_t)xn;
#    if _N_IS_SHAPE
        view->shape = (Py_ssize_t *)&xn;
#    else
        view->shape = malloc(sizeof(Py_ssize_t));
        view->shape[0] = (Py_ssize_t)xn;
#    endif
        view->strides = &view->itemsize;
        view->suboffsets = NULL;

        view->buf = xG;
        view->readonly = (x->u != 0);
    }
    else if (xt < 0) {
        view->ndim = 0;
        view->itemsize = itemsize;
        view->format = (flags & PyBUF_FORMAT) ? k_format(-xt) : NULL;
        view->len = itemsize;
        view->shape = view->strides = view->suboffsets = NULL;
#    if KXVER >= 3
        if (xt == -UU)
            view->buf = x->G0;
        else
#    endif
            view->buf = &x->g;
        view->readonly = 0;
    }
    else {
        static Py_ssize_t suboffsets[2] = {
            offsetof(struct k0, G0),
            offsetof(struct k0, G0),
        };
        H t;
        J m;
        I i;

        /* Support rectangular 2d arrays only for now */
        if (xn == 0) {
            PyErr_SetString(PyExc_BufferError, "empty generic list");
            return -1;
        }
        t = xK[0]->t;
        m = xK[0]->n;
        if (t < 0) {
            PyErr_SetString(PyExc_BufferError, "scalar in generic list");
            return -1;
        }
        for (i = 1; i < xn; ++i) {
            if (t != xK[i]->t) {
                PyErr_SetString(PyExc_BufferError, "type varies");
                return -1;
            }
            if (m != xK[i]->n) {
                PyErr_SetString(PyExc_BufferError, "size varies");
                return -1;
            }
        }

        itemsize = k_itemsize(xx);
        view->ndim = 2;
        view->itemsize = itemsize;
        view->format = (flags & PyBUF_FORMAT) ? k_format(t) : NULL;
        view->len = (Py_ssize_t)m * (Py_ssize_t)xn * itemsize;

        view->shape = malloc(2 * sizeof(Py_ssize_t));
        view->shape[0] = (Py_ssize_t)xn;
        view->shape[1] = (Py_ssize_t)m;

        view->suboffsets = suboffsets;
        view->strides = malloc(2 * sizeof(Py_ssize_t));
        view->strides[0] = sizeof(K);
        view->strides[1] = itemsize;

        view->buf = xG;
        view->readonly = 0;
    }
    Py_INCREF(self);
    view->obj = (PyObject *)self;
    return 0; /* 0 - success / -1 - failure */
}

static int
K_buffer_getbuffer(KObject *self, Py_buffer *view, int flags)
{
    return _k_getbuffer(self, view, flags, 0);
}

static void
K_buffer_releasebuffer(KObject *self, Py_buffer *view)
{
    if (view->ndim > 1) {
        free(view->shape);
        free(view->strides);
    }
#if !_N_IS_SHAPE
    else if (view->ndim == 1) {
        free(view->shape);
    }
#endif
    return;
}

static Py_ssize_t
klen(K x)
{
    if (xt < 0)
        return 1;
    if (xt < 98)
        return (Py_ssize_t)xn;
    switch (xt) {
    case 99: /* dict */
        if (xx->t == 98)
            x = xx;
        else
            return (Py_ssize_t)xx->n;
        /* fall through */
    case 98: /* flip */
        return (Py_ssize_t)kK(kK(x->k)[1])[0]->n;
    }
    return 1;
}

static int
K_bool(KObject *v)
{
    K x = v->x;
    I t = xt;
    if (t >= 0) {
        if (t < 100) /* lists */
            return klen(x) > 0;
        else if (t == 101 && xj == 0)
            return 0;
        else
            return 1;
    }
    /* scalars */
    switch (-t) {
    case KB:
    case KG:
    case KC:
        return xg != 0;
    case KJ:
    case KN:
        return xj != 0;
    case KS:
        /* XXX: Can optimize to x != null_sym */
        return xs[0] != 0;
    case KH:
        return xh != 0;
    case KI:
    case KU:
    case KV:
    case KT:
        return xi != 0;
    case KE:
        return xe != 0;
    case KF:
        return xf != 0;
    }
    if (t < -19) {
        int res;
        x = k(0, "value", r1(x), (K)0);
        if (xt == -KS) {
            res = xs[0] != 0;
        }
        else if (xt == -128) {
            PyErr_SetString(ErrorObject, xs ? xs : (S) "not set");
            res = -1;
        }
        else {
#if KX36
            if (t == -20) {
                assert(xt == -KJ);
                res = xj != nj;
            }
            else
#endif
            {
                assert(xt == -KI);
                res = xi != ni;
            }
        }
        r0(x);
        return res;
    }
    return 1;
}

static PyNumberMethods K_as_number = {
    0, /*nb_add*/
    0, /*nb_subtract*/
    0, /*nb_multiply*/
    0,               /*nb_remainder*/
    0,               /*nb_divmod*/
    0,               /*nb_power*/
    0,               /*nb_negative*/
    0,               /*nb_positive*/
    0,               /*nb_absolute*/
    (inquiry)K_bool, /*nb_bool*/
    0,               /*nb_invert*/
    0,               /*nb_lshift*/
    0,               /*nb_rshift*/
    0,               /*nb_and*/
    0,               /*nb_xor*/
    0,               /*nb_or*/
    0,               /*nb_int*/
    0,               /*nb_reserved*/
    0,               /*nb_float*/
};

static Py_ssize_t
K_length(KObject *k)
{
    return klen(k->x);
}

static PyObject *getitem(PyTypeObject *ktype, K x, Py_ssize_t i);

static PyObject *
K_item(KObject *k, Py_ssize_t i)
{
    return getitem(Py_TYPE(k), k->x, i);
}

static PySequenceMethods K_as_sequence = {
    (lenfunc)K_length,    /* sq_length */
    (binaryfunc)0,        /* sq_concat */
    (ssizeargfunc)0,      /* sq_repeat */
    (ssizeargfunc)K_item, /* sq_item */
};


static PyBufferProcs K_as_buffer = {
    (getbufferproc)K_buffer_getbuffer,
    (releasebufferproc)K_buffer_releasebuffer,
};

static PyObject *
K_get_r(KObject *self)
{
    K x = self->x;
    return PyLong_FromLong(xr);
}

static PyObject *
K_get_t(KObject *self)
{
    K x = self->x;
    return PyLong_FromLong(xt);
}

static PyObject *
K_get_n(KObject *self)
{
    K x = self->x;
    if (xt >= 0 && xt != 98)
        return PyLong_FromLongLong(xn);
    PyErr_Format(PyExc_AttributeError,
                 "K object of type %dh does not have '_n' attribute",
                 xt);
    return NULL;
}

static PyObject *
K_get_data(KObject *self)
{
    PyMemoryViewObject *mv;
    Py_buffer view;
    K x = self->x;
    char typechar = k_typekind(x);
    if (typechar == 'X' || xt == 0) {
        PyErr_Format(PyExc_AttributeError,
                     "K object of type %dh does not have 'data' attribute",
                     xt);
        return NULL;
    }
    if (_k_getbuffer(self, &view, PyBUF_FULL, 1) == -1)
        return NULL;
    mv = (PyMemoryViewObject *)PyMemoryView_FromBuffer(&view);
    if (mv == NULL) {
        K_buffer_releasebuffer(self, &view);
        Py_DECREF(self);
        return NULL;
    }
    /* PyMemoryView_FromBuffer sets obj to NULL in both mv and
       the master buffer, so we have to restore them ourselves. */
    mv->view.obj = (PyObject *)self;
    mv->mbuf->master.obj = (PyObject *)self;
    return (PyObject *)mv;
}

static PyGetSetDef K_getset[] = {
    {"_r", (getter)K_get_r, NULL, "K object reference count"},
    {"_t", (getter)K_get_t, NULL, "K object type"},
    {"_n", (getter)K_get_n, NULL, "K object element count"},
    {"__array_struct__",
     (getter)K_array_struct_get,
     NULL,
     "Array protocol: struct"},
    {"__array_typestr__",
     (getter)K_array_typestr_get,
     NULL,
     "Array protocol: typestr"},
    {"data", (getter)K_get_data, NULL, "Return memoryview."},
    {NULL, NULL, NULL, NULL}, /* Sentinel */
};

static PyObject *k_iter(KObject *o);
#if KXVER > 2
#    define K_INT kj
#else
#    define K_INT ki
#endif
ZK
py2k(PyObject *obj)
{
    K x = NULL;
    /* check for singletons first */
    if (obj == Py_None)
        x = r1(k_none); /* (::) */
    else if (obj == Py_False)
        x = kb(0);
    else if (obj == Py_True)
        x = kb(1);
    else if (PyUnicode_Check(obj)) {
        S s;
        PY_SET_SN(s, obj);
        x = ks(s);
    }
    else if (PyFloat_Check(obj))
        x = kf(PyFloat_AS_DOUBLE(obj));
    else if (PyLong_CheckExact(obj)) {
        J j = PyLong_AsLongLong(obj);
        if (j == -1 && PyErr_Occurred())
            return NULL;
        x = K_INT(j);
    }
    R x;
}

/* Returns a new reference or NULL on error */
static PyObject *
get_base_object(PyObject *capsule)
{
    PyObject *base, *tmp;
    base = (PyObject *)PyCapsule_GetContext(capsule);
    base = PyObject_GetAttrString(base, "base");
    if (!PyMemoryView_Check(base)) {
        Py_DECREF(base);
        Py_RETURN_NONE;
    }
    tmp = base;
    base = PyMemoryView_GET_BASE(base);
    Py_INCREF(base);
    Py_DECREF(tmp);
    return base;
}

static PyObject *
K_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    K x;
    PyObject *obj, *attr;

    if (!PyArg_ParseTuple(args, "O:K", &obj))
        return NULL;
    if (K_Check(obj)) {
        Py_INCREF(obj);
        return obj;
    }
    x = py2k(obj);
    if (x) {
        return KObject_FromK(type, x);
    }
    if (PyErr_Occurred()) {
        return NULL;
    }
    if (PyDateTime_Check(obj)) {
        return K_kpz(type, obj);
    }
    if (PyDelta_Check(obj)) {
        return K_knz(type, obj);
    }
    if (PyDate_Check(obj)) {
        return K_kd(type, obj);
    }
    if (PyTime_Check(obj)) {
        return K_kt(type, obj);
    }
    attr = PyObject_GetAttrString(obj, "__array_struct__");
    if (attr == NULL) {
        if (PyErr_ExceptionMatches(PyExc_AttributeError)) {
            PyErr_Clear();
        }
        else {
            return NULL;
        }
    }
    else {
        PyObject *r = NULL, *mask, *base;
        base = get_base_object(attr);
        if (base == NULL || K_Check(base)) {
            Py_DECREF(attr);
            return base;
        }
        else {
            Py_DECREF(base);
        }
        x = _from_array_struct(type, attr);
        Py_DECREF(attr);
        if (x == NULL) {
            if (PyErr_ExceptionMatches(PyExc_NotImplementedError)) {
                PyErr_Clear();
            }
            else {
                return NULL;
            }
            PyErr_Clear();
            r = PyObject_CallMethod(
                (PyObject *)type, "_from_record_array", "(O)", obj);
            if (r == NULL) {
                Py_DECREF(attr);
                return NULL;
            }
        }
        mask = PyObject_GetAttrString(obj, "mask");
        if (mask == NULL) {
            if (PyErr_ExceptionMatches(PyExc_AttributeError)) {
                PyErr_Clear();
            }
            else {
                return NULL;
            }
        }
        else {
            PyObject *tmp = r;
            r = KObject_FromK(type, x);
            if (r == NULL) {
                Py_XDECREF(tmp);
                Py_DECREF(mask);
                return NULL;
            }
            tmp = r;
            r = PyObject_CallMethod(r, "_set_mask", "(O)", mask);
            Py_XDECREF(tmp);
            Py_DECREF(mask);
            return r;
        }
        return x ? KObject_FromK(type, x) : r;
    }

    return PyObject_CallMethod((PyObject *)type, "_convert", "(O)", obj);
    ;
}

static PyObject *
K_descr_get(KObject *self, PyObject *obj, PyTypeObject *type)
{
    K x, y;
    if (obj == NULL || !K_Check(obj)) {
        Py_INCREF(self);
        return (PyObject *)self;
    }
    x = self->x;
    y = ((KObject *)obj)->x;
    return KObject_FromK(type, k(0, "@", r1(x), r1(y), (K)0));
}

static PyTypeObject K_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "pyq._k.K", /*tp_name */
    sizeof(KObject),                           /*tp_basicsize */
    0,                                         /*tp_itemsize */
    /* methods */
    (destructor)K_dealloc, /*tp_dealloc */
    0,                     /*tp_print */
    0,                     /*tp_getattr */
    0,                     /*tp_setattr */
    0,                     /*tp_compare */
    (reprfunc)K_repr,      /*tp_repr */
    &K_as_number,          /*tp_as_number */
    &K_as_sequence,        /*tp_as_sequence */
    0,                     /*tp_as_mapping */
    0,                     /*tp_hash */
    (ternaryfunc)K_call,   /*tp_call */
    (reprfunc)K_str,       /*tp_str */
    0,                     /*tp_getattro */
    0,                     /*tp_setattro */
    &K_as_buffer,          /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT
        | Py_TPFLAGS_BASETYPE, /*tp_flags */
    0,                         /*tp_doc */
    0,                         /*tp_traverse */
    0,                         /*tp_clear */
    0,                         /*tp_richcompare */
    0,                         /*tp_weaklistoffset */
    (getiterfunc)k_iter,       /*tp_iter */
    0,                         /*tp_iternext */
    K_methods,                 /*tp_methods */
    0,                         /*tp_members */
    K_getset,                  /*tp_getset */
    0,                         /*tp_base */
    0,                         /*tp_dict */
    (descrgetfunc)K_descr_get, /*tp_descr_get */
    0,                         /*tp_descr_set */
    0,                         /*tp_dictoffset */
    (initproc)0,               /*tp_init */
    0,                         /*tp_alloc */
    K_new,                     /*tp_new */
    0,                         /*tp_free */
    0,                         /*tp_is_gc */
};

/* --------------------------------------------------------------------- */

#if 0
PyDoc_STRVAR(_k_khp_doc,
             "khp(host,port) -> connection handle\n"
             "\n>>> c = khp('localhost', 5001)\n");

static PyObject *
_k_khp(PyObject *self, PyObject *args)
{
    char *h;

    int p;

    if (!PyArg_ParseTuple(args, "si:khp", &h, &p))
        return NULL;
    return PyLong_FromLong(khp(h, p));
}
#endif

PyDoc_STRVAR(_k_ymd_doc, "ymd(y,m,d) -> q date\n\n>>> ymd(2000, 1, 1)\n0\n");

static PyObject *
_k_ymd(PyObject *self, PyObject *args)
{
    int y, m, d;

    if (!PyArg_ParseTuple(args, "iii:ymd", &y, &m, &d))
        return NULL;
    return PyLong_FromLong(ymd(y, m, d));
}

PyDoc_STRVAR(_k_dj_doc, "dj(j) -> yyyymmdd (as int)\n");
static PyObject *
_k_dj(PyObject *self, PyObject *args)
{
    int j;

    if (!PyArg_ParseTuple(args, "i:dj", &j))
        return NULL;
    return PyLong_FromLong(dj(j));
}

PyDoc_STRVAR(_k_okx_doc,
             "okx(x) -> bool\n\n"
             "Return True if x is well-formed IPC byte vector.\n");
static PyObject *
_k_okx(PyObject *self, KObject *arg)
{
    K x;
    if (!K_Check(arg)) {
        PyErr_Format(PyExc_TypeError,
                     "Expected a K object, not %100s",
                     Py_TYPE(arg)->tp_name);
        return NULL;
    }
    x = arg->x;
    if (xt != KG) {
        PyErr_Format(PyExc_TypeError,
                     "Expected a K object of type 4 (bytes), not %dh",
                     xt);
        return NULL;
    }
    return PyBool_FromLong(okx(x));
}

#if KXVER >= 3
PyDoc_STRVAR(_k_m9_doc,
             "m9()\n\n"
             "Free up memory allocated for the thread's pool.\n");
static PyObject *
_k_m9(PyObject *self)
{
    m9();
    Py_RETURN_NONE;
}

PyDoc_STRVAR(_k_setm_doc,
             "setm(f) -> int\n\n"
             "Set whether interning symbols uses a lock.\n");
static PyObject *
_k_setm(PyObject *self, PyObject *arg)
{
    Py_ssize_t f;

    f = PyNumber_AsSsize_t(arg, NULL);
    if (f == -1 && PyErr_Occurred())
        return NULL;
    return PyLong_FromLong(setm(f != 0));
}
#endif /* KXVER>=3 */

/* List of functions defined in the module */
static PyMethodDef _k_methods[] = {
    {"sd0", (PyCFunction)K_sd0, METH_VARARGS, K_sd0_doc},
    {"sd1", (PyCFunction)K_sd1, METH_VARARGS, K_sd1_doc},
    {"ymd", _k_ymd, METH_VARARGS, _k_ymd_doc},
    {"dj", _k_dj, METH_VARARGS, _k_dj_doc},
    {"okx", (PyCFunction)_k_okx, METH_O, _k_okx_doc},
#if KXVER >= 3
    {"m9", (PyCFunction)_k_m9, METH_NOARGS, _k_m9_doc},
    {"setm", (PyCFunction)_k_setm, METH_O, _k_setm_doc},
#endif           /* KXVER>=3 */
    {NULL, NULL} /* sentinel */
};

/*********************** K Object Iterator **************************/

typedef struct {
    PyObject_HEAD PyTypeObject *ktype;
    K x;
    J i, n;
} kiterobject;

static PyTypeObject KObjectIter_Type;

#define KObjectIter_Check(op) PyObject_TypeCheck(op, &KObjectArrayIter_Type)

static PyObject *
k_iter(KObject *obj)
{
    kiterobject *it;

    K x = obj->x;

    if (xt < 0) {
        PyErr_Format(
            PyExc_TypeError, "iteration over a K scalar, t=%d", (int)xt);
        return NULL;
    }

    it = PyObject_New(kiterobject, &KObjectIter_Type);
    if (it == NULL)
        return NULL;
    Py_INCREF(it->ktype = Py_TYPE(obj));

    if (xt == XD)
        x = xx;
    it->x = r1(x);
    it->i = 0;
    if (!k_itemsize(x) && xt != XT) {
        PyErr_Format(PyExc_NotImplementedError, "not iterable: t=%d", (int)xt);
        return NULL;
    }
    it->n = xt == XT ? kK(kK(xk)[1])[0]->n : xn;

    return (PyObject *)it;
}

static PyObject *
d2py(I d)
{
    div_t x;
    I ymd, y, m;

    switch (d) {
    case -wi:
        R PyDate_FromDate(1, 1, 1);
    case wi:
        R PyDate_FromDate(9999, 12, 31);
    case ni:
        Py_RETURN_NONE;
    }
    ymd = dj(d);
    x = div(ymd, 10000);
    y = x.quot;
    x = div(x.rem, 100);
    m = x.quot;
    d = x.rem;

    R PyDate_FromDate(y, m, d);
}

static PyObject *
m2py(I m)
{
    div_t x;
    switch (m) {
    case -wi:
        R PyDate_FromDate(1, 1, 1);
    case wi:
        R PyDate_FromDate(9999, 12, 1);
    case ni:
        Py_RETURN_NONE;
    }
    x = div(2000 * 12 + m, 12);
    return PyDate_FromDate(x.quot, 1 + x.rem, 1);
}

static PyObject *
z2py(F z)
{
    if (isfinite(z)) {
        div_t x;
        I ymd, y, m, d;
        I h, u, s, ms;
        F f;

        if (z > 0) {
            f = fmod(z, 1);
        }
        else {
            f = 1 + fmod(z, 1);
        }
        ymd = dj((I)(z - f));

        x = div(ymd, 10000);
        y = x.quot;
        x = div(x.rem, 100);
        m = x.quot;
        d = x.rem;

        ms = (I)round(24 * 60 * 60 * 1000 * f);
        x = div(ms, 1000);
        ms = x.rem;
        x = div(x.quot, 60);
        s = x.rem;
        x = div(x.quot, 60);
        u = x.rem;
        h = x.quot;

        return PyDateTime_FromDateAndTime(y, m, d, h, u, s, ms * 1000);
    }
    if (isnan(z))
        Py_RETURN_NONE;
    return z < 0
        ? PyDateTime_FromDateAndTime(1, 1, 1, 0, 0, 0, 0)
        : PyDateTime_FromDateAndTime(9999, 12, 31, 23, 59, 59, 999999);
}

static PyObject *
t2py(I t)
{
    div_t x;
    I h, m, s, ms;
    switch (t) {
    case ni:
        Py_RETURN_NONE;
    case -wi:
    case wi:
        R PyErr_Format(PyExc_OverflowError, "infinite time");
    }
    x = div(t, 1000);
    ms = x.rem;
    x = div(x.quot, 60);
    s = x.rem;
    x = div(x.quot, 60);
    m = x.rem;
    x = div(x.quot, 60);
    h = x.rem;
    return PyTime_FromTime(h, m, s, 1000 * ms);
}

static PyObject *
v2py(I t)
{
    div_t x;
    I h, m, s;
    switch (t) {
    case ni:
        Py_RETURN_NONE;
    case -wi:
    case wi:
        R PyErr_Format(PyExc_OverflowError, "infinite seconds");
    }
    x = div(t, 60);
    s = x.rem;
    x = div(x.quot, 60);
    m = x.rem;
    x = div(x.quot, 60);
    h = x.rem;
    return PyTime_FromTime(h, m, s, 0);
}

static PyObject *
u2py(I t)
{
    div_t x;
    I h, m;
    switch (t) {
    case ni:
        Py_RETURN_NONE;
    case -wi:
    case wi:
        R PyErr_Format(PyExc_OverflowError, "infinite minutes");
    }
    x = div(t, 60);
    m = x.rem;
    x = div(x.quot, 60);
    h = x.rem;
    return PyTime_FromTime(h, m, 0, 0);
}

static PyObject *
getitem(PyTypeObject *ktype, K x, Py_ssize_t i)
{
    PyObject *ret = NULL;
    Py_ssize_t n = klen(x);
    /* NB: Negative indexes are handled as follows: if the sq_length
       slot is filled (our case), it is called and the sequence length
       is used to compute a positive index which is passed to sq_item. */
    if (i >= n || i < 0) {
        PyErr_SetString(PyExc_IndexError, "k index out of range");
        return NULL;
    }

    switch (xt) {
    case KS: /* most common case: use list(ks) */
        ret = PyUnicode_InternFromString(xS[i]);
        break;
    case 0:
        ret = KObject_FromK(ktype, r1(xK[i]));
        break;
#if KXVER >= 3
    case UU:
        ret = _PyLong_FromByteArray(xU[i].g, 16, 0, 0);
        break;
#endif
        /* remaining cases are less common because array(x) *
         * is a better option that list(x)                  */
    case KB:
        ret = PyBool_FromLong(xG[i]);
        break;
    case KC:
        ret = PyUnicode_FromStringAndSize((S)&xC[i], 1);
        break;
    case KG:
        ret = PyLong_FromLong(xG[i]);
        break;
    case KH:
        ret = xH[i] == nh ? Py_INCREF(Py_None),
        Py_None : PyLong_FromLong(xH[i]);
        break;
    case KI:
        ret = xI[i] == ni ? Py_INCREF(Py_None),
        Py_None : PyLong_FromLong(xI[i]);
        break;
    case KM:
        ret = m2py(xI[i]);
        break;
    case KD:
        ret = d2py(xI[i]);
        break;
    case KV:
        ret = v2py(xI[i]);
        break;
    case KU:
        ret = u2py(xI[i]);
        break;
    case KT:
        ret = t2py(xI[i]);
        break;
    case KZ:
        ret = z2py(xF[i]);
        break;
    case KJ:
        ret = xJ[i] == nj ? Py_INCREF(Py_None),
        Py_None : PyLong_FromLongLong(xJ[i]);
        break;
    case KE:
        ret = PyFloat_FromDouble(xE[i]);
        break;
    case KF:
        ret = PyFloat_FromDouble(xF[i]);
        break;
    case XT:
        ret = KObject_FromK(ktype, k(0, "@", r1(x), kj(i), (K)0));
        break;
#if KX36
    case 20: { /* 64-bit enums */
        J j = xJ[i];
        K key = k(0, "{value key x}", r1(x), (K)0);
        if (key->t == KS) {
            ret = PyUnicode_InternFromString(j < key->n && j >= 0 ?
                                          kS(key)[j] : "");
        }
        r0(key);
        break;
    }
#endif
    default:
        if (xt >= 20 && xt < ENUMS_END) {
            /* In kdb+ version >= 3.6, this can only be reached when
               xt >= 21 corresponding to legacy 32-bit enums. */
            I j = xI[i];
            K key = k(0, "{value key x}", r1(x), (K)0);
            if (key->t == KS) {
                ret = PyUnicode_InternFromString(j < key->n && j >= 0 ?
                                              kS(key)[j] : "");
            }
            r0(key);
        }
    }
    if (ret == NULL)
        PyErr_SetString(PyExc_NotImplementedError, "not implemented");
    return ret;
}

static PyObject *
kiter_next(kiterobject *it)
{
    PyObject *ret = NULL;

    K x = it->x;

    J i = it->i, n = it->n;

    if (i < n)
        ret = getitem(it->ktype, x, (Py_ssize_t)i);
    it->i++;
    return ret;
}

static void
kiter_dealloc(kiterobject *it)
{
    Py_XDECREF(it->ktype);
    r0(it->x);
    PyObject_Del(it);
}

static PyTypeObject KObjectIter_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "kiterator", /* tp_name */
    sizeof(kiterobject),                        /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)kiter_dealloc,               /* tp_dealloc */
    0,                                       /* tp_print */
    0,                                       /* tp_getattr */
    0,                                       /* tp_setattr */
    0,                                       /* tp_compare */
    0,                                       /* tp_repr */
    0,                                       /* tp_as_number */
    0,                                       /* tp_as_sequence */
    0,                                       /* tp_as_mapping */
    0,                                       /* tp_hash */
    0,                                       /* tp_call */
    0,                                       /* tp_str */
    PyObject_GenericGetAttr,                 /* tp_getattro */
    0,                                       /* tp_setattro */
    0,                                       /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                      /* tp_flags */
    0,                                       /* tp_doc */
    0,            /* tp_traverse */
    0,                                       /* tp_clear */
    0,                                       /* tp_richcompare */
    0,                                       /* tp_weaklistoffset */
    PyObject_SelfIter,                       /* tp_iter */
    (iternextfunc)kiter_next,                /* tp_iternext */
    0,                                       /* tp_methods */
};

static PyObject *
K_pys(KObject *self)
{
    K x = self->x;
    if (xt >= 0) {
        PyErr_SetString(PyExc_TypeError, "not a scalar");
        return NULL;
    }
    switch (xt) {
    case -KB:
        return PyBool_FromLong(xg);
    case -KC:
        return PyUnicode_FromStringAndSize((S)&xg, 1);
    case -KG:
        return PyLong_FromLong(xg);
    case -KH:
        return PyLong_FromLong(xh);
    case -KI:
        return PyLong_FromLong(xi);
    case -KJ:
        return PyLong_FromLongLong(xj);
    case -KE:
        return PyFloat_FromDouble(xe);
    case -KF:
        return PyFloat_FromDouble(xf);
    case -KS:
        return PyUnicode_FromString(xs);
    case -KD:
        return d2py(xi);
    case -KM:
        return m2py(xi);
    case -KT:
        return t2py(xi);
    case -KU:
        return u2py(xi);
    case -KV:
        return v2py(xi);
    case -KZ:
        return z2py(xf);
    }
    PyErr_SetString(PyExc_NotImplementedError, "not implemented");
    return NULL;
}

/* Initialization function for the _k module */
PyMODINIT_FUNC PyInit__k(void)
{
    PyObject *m;
    K x;

    PyDateTime_IMPORT;
    k_none = k(0, "::", (K)0);
    k_nil = k(0, "last value(;)", (K)0);
    k_repr = k(0, "-3!", (K)0);
    k_noargs = knk(1, r1(k_none));
    ns = ss("");
    debug = getenv("PYQDBG") != NULL;
    /* trp support */
    get_backtrace_dl = dl(get_backtrace, 2);
    /* PEP 3118 */
    k_types['?'] = KB;
    k_types['B'] = KG;
    k_types['h'] = KH;
    k_types['i'] = KI;
    k_types['q'] = KJ;
    k_types['f'] = KE;
    k_types['d'] = KF;

    /* Create the module and add the functions */
    static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "pyq._k", module_doc, -1, _k_methods};
    m = PyModule_Create(&moduledef);
    if (m == NULL)
        return NULL;

    /* Finalize the type object including setting type of the new type
     * object; doing it here is required for portability to Windows
     * without requiring C++. */
    if (PyType_Ready(&K_Type) < 0)
        return NULL;

    /* Add some symbolic constants to the module */
    if (ErrorObject == NULL) {
        ErrorObject = PyErr_NewException("_k.error", NULL, NULL);
        if (ErrorObject == NULL)
            return NULL;
    }
    Py_INCREF(ErrorObject);
    PyModule_AddObject(m, "error", ErrorObject);

    /* Add K */
    PyModule_AddObject(m, "K", (PyObject *)&K_Type);
    /* vector types */
    PyModule_AddIntMacro(m, KB);
#if KXVER >= 3
    PyModule_AddIntMacro(m, UU);
#endif
    PyModule_AddIntMacro(m, KG);
    PyModule_AddIntMacro(m, KH);
    PyModule_AddIntMacro(m, KI);
    PyModule_AddIntMacro(m, KJ);
    PyModule_AddIntMacro(m, KE);
    PyModule_AddIntMacro(m, KF);
    PyModule_AddIntMacro(m, KC);
    PyModule_AddIntMacro(m, KS);
    PyModule_AddIntMacro(m, KP);
    PyModule_AddIntMacro(m, KM);
    PyModule_AddIntMacro(m, KD);
    PyModule_AddIntMacro(m, KN);
    PyModule_AddIntMacro(m, KZ);
    PyModule_AddIntMacro(m, KU);
    PyModule_AddIntMacro(m, KV);
    PyModule_AddIntMacro(m, KT);
    /* table, dict */
    PyModule_AddIntMacro(m, XT);
    PyModule_AddIntMacro(m, XD);

    PyModule_AddIntConstant(m, "SIZEOF_VOID_P", SIZEOF_VOID_P);
    PyModule_AddStringConstant(m, "__version__", __version__);

    x = k(0, ".z.K", (K)0);
    assert(xt == -KF);
    PyModule_AddObject(m, "Q_VERSION", PyFloat_FromDouble(xf));
    r0(x);

    x = k(0, ".z.k", (K)0);
    assert(xt == -KD);
    PyModule_AddObject(m, "Q_DATE", d2py(xi));
    r0(x);

    x = k(0, ".z.o", (K)0);
    assert(xt == -KS);
    PyModule_AddStringConstant(m, "Q_OS", xs);
    r0(x);

    return m;
}
