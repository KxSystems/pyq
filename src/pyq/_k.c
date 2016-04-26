/* -*- mode: c; c-basic-offset: 4 -*- */
static char __version__[] = "$Revision: 10002$";

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
#include "Python.h"
#include "datetime.h"
#include "longintrepr.h"

#include "k.h"
#include <math.h>
#if defined (WIN32) || defined(_WIN32)
    #define isfinite _finite
    double round(double d)
        {
          return floor(d + 0.5);
        }
#endif
#include <stddef.h>
#include <stdlib.h>
#include <float.h>

/* Macrobatics */
#define CAT(x, y) x##y
#define XCAT(x, y) CAT(x, y)
#define SCAT(x, y) (x #y)
#define XSCAT(x, y) SCAT(x, y)
#define SCAT3(x, y, z) (x #y z)
#define XSCAT3(x, y, z) SCAT3(x, y, z)

/* vvv Py3K compatibility vvv */
#if PY_MAJOR_VERSION >= 3

#    define PyInt_AsLong PyLong_AsLong
#    define PyInt_FromLong PyLong_FromLong

#    define PyString_FromStringAndSize PyBytes_FromStringAndSize
#    define PyString_AsStringAndSize PyBytes_AsStringAndSize
#    define PyString_FromString PyBytes_FromString

#    define PY_STR_Check PyUnicode_Check
#    define PY_STR_FromString PyUnicode_FromString
#    define PY_STR_InternFromString PyUnicode_InternFromString
#    define PY_STR_FromFormat PyUnicode_FromFormat
#    define PY_STR_Format PyUnicode_Format
#    define PY_STR_FromStringAndSize PyUnicode_FromStringAndSize

#define PY_SET_SN(var, obj) {                                   \
        Py_ssize_t size;                                        \
        char *str = _PyUnicode_AsStringAndSize(obj, &size);     \
        var = sn(str, size);                                    \
        }

static int
PY_STR_AsStringAndSize(PyObject *obj, char **str, Py_ssize_t * size)
{
    *str = _PyUnicode_AsStringAndSize(obj, size);
    return str ? 0 : -1;
}

#    define MOD_ERROR_VAL NULL
#    define MOD_SUCCESS_VAL(val) val
#    define MOD_INIT(name) PyMODINIT_FUNC XCAT(PyInit_##name, QVER)(void)
#    define MOD_DEF(ob, name, doc, methods)                       \
        static struct PyModuleDef moduledef = {                   \
                PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
        ob = PyModule_Create(&moduledef);
#else /* PY_MAJOR_VERSION >= 3 */

#    define PY_STR_Check PyString_Check
#    define PY_STR_FromString PyString_FromString
#    define PY_STR_InternFromString PyString_InternFromString
#    define PY_STR_FromFormat PyString_FromFormat
#    define PY_STR_Format PyString_Format
#    define PY_STR_FromStringAndSize PyString_FromStringAndSize
#    define PY_STR_AsStringAndSize PyString_AsStringAndSize

#define PY_SET_SN(var, obj) var = sn(PyString_AS_STRING(obj),   \
                                     PyString_GET_SIZE(obj));

#    define MOD_ERROR_VAL
#    define MOD_SUCCESS_VAL(val)
#    define MOD_INIT(name) void XCAT(init##name, QVER)(void)
#    define MOD_DEF(ob, name, doc, methods)             \
        ob = Py_InitModule3(name, methods, doc);
#endif /* PY_MAJOR_VERSION >= 3 */
/* ^^^ Py3K compatibility ^^^ */

/* these should be in k.h */
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

#include <stdlib.h>
typedef struct {
    PyObject_HEAD K x;
} KObject;

static PyTypeObject K_Type;

#define K_Check(op) PyObject_TypeCheck(op, &K_Type)
#define K_CheckExact(op) (Py_TYPE(op) == &K_Type)

#include <stdio.h>
#include <ctype.h>
#ifndef  Py_RETURN_NONE
#   define Py_RETURN_NONE Py_INCREF(Py_None); return Py_None
#endif
#if PY_VERSION_HEX < 0x2050000
typedef int Py_ssize_t;

typedef Py_ssize_t(*readbufferproc) (PyObject *, Py_ssize_t, void **);

typedef Py_ssize_t(*writebufferproc) (PyObject *, Py_ssize_t, void **);

typedef Py_ssize_t(*segcountproc) (PyObject *, Py_ssize_t *);

#define PyInt_FromSsize_t PyInt_FromLong
#endif

PyDoc_STRVAR(module_doc,
             "Low level q interface module.\n"
             "\n"
             "Provides a K object - python handle to q datatypes.\n"
             "\n"
             "This module is implemented as a thin layer on top of C API, k.h.  Most\n"
             "functions described in http://kx.com/q/c/c.txt are\n"
             "implemented as methods of the K class.  Names of the functions are formed by\n"
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
             "c  1    " "          char      unsigned char    \n"
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
static K k_none;

static PyObject *ErrorObject;

/* always consumes x reference */
static PyObject *
KObject_FromK(PyTypeObject * type, K x)
{
    KObject *self;

    if (!type)
        type = &K_Type;
    if (x == NULL) {
        PyErr_SetString(PyExc_SystemError, "attempted to create null K object");
        R NULL;
    }
    if (xt == -128) {
        PyErr_SetString(ErrorObject, xs ? xs : (S) "not set");
        R r0(x), NULL;
    }
    self = (KObject *) type->tp_alloc(type, 0);
    if (self)
        self->x = x;
    else
        r0(x);

    R (PyObject *) self;
}

/* converter function */
static int
getK(PyObject *arg, void *addr)
{
    K r;
    if (!K_Check(arg)) {
        return PyErr_BadArgument();
    }
    r = ((KObject *) arg)->x;

    /*
       if (!r) {
       return PyErr_BadArgument();
       }
     */
    *(K *) addr = r;
    return 1;
}

static void
K_dealloc(KObject * self)
{
    if (self->x) {
        r0(self->x);
    }
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
K_dot(KObject * self, PyObject *args)
{
    R K_Check(args)
    ? KObject_FromK(Py_TYPE(self),
                    k(0, ".", r1(self->x), r1(((KObject *) args)->x), (K) 0))
    : PyErr_Format(PyExc_TypeError, "expected a K object, not %s",
                   Py_TYPE(args)->tp_name);
}

/* extern K a1(K,K); */
static PyObject *
K_a0(KObject * self)
{
    K x = self->x;

    if (xt < 100) {
        Py_INCREF(self);
        return (PyObject *)self;
    }
    R KObject_FromK(Py_TYPE(self), k(0, "@", r1(x), r1(k_none), (K) 0));
}

static PyObject *
K_a1(KObject * self, PyObject *arg)
{
    R K_Check(arg)
    ? KObject_FromK(Py_TYPE(self),
                    k(0, "@", r1(self->x), r1(((KObject *) arg)->x), (K) 0))
    : PyErr_Format(PyExc_TypeError, "expected a K object, not %s",
                   Py_TYPE(arg)->tp_name);
}

static PyObject *
K_ja(KObject * self, PyObject *arg)
{
    switch (self->x->t) {
    case 0:{
            if (K_Check(arg))
                jk(&self->x, r1(((KObject *) arg)->x));
            else
                R PyErr_Format(PyExc_TypeError,
                               "K._ja: expected K object, not %s",
                               Py_TYPE(arg)->tp_name);
            break;
        }
    case KB:{
            if (PyBool_Check(arg)) {
                G a = (arg == Py_True);

                ja(&self->x, &a);
            }
            else
                R PyErr_Format(PyExc_TypeError, "K._ja: expected bool, not %s",
                               Py_TYPE(arg)->tp_name);
            break;
        }
    case KG:{
            G g;
            long a = PyInt_AsLong(arg);

            if (a == -1 && PyErr_Occurred())
                R NULL;
            if (a < 0 || a > 257) {
                PyErr_Format(PyExc_OverflowError, "Expected an integer between 0 and 257, not %ld", a);
                R NULL;
            }
            g = (G)a;
            ja(&self->x, &g);
            break;
        }
    case KH:{
            H h;
            long a = PyInt_AsLong(arg);
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
    case KI:{
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
    case KJ:{
            int overflow;
            J j;
            long long a = PyLong_AsLongLongAndOverflow(arg, &overflow);
            if (a == -1) {
                if (PyErr_Occurred()) {
                    if (arg == Py_None) {
                        PyErr_Clear();
                        j = nj;
                    }
                    else
                        R NULL;
                } else if (overflow) {
                    j = overflow * wj;
                }
            }
            else
                j = (J)a;
            ja(&self->x, &j);
            break;
        }
    case KE:{
            E e;
            double a = PyFloat_AsDouble(arg);
            if (a == -1 && PyErr_Occurred()) {
                if (arg == Py_None) {
                     PyErr_Clear();
                     e = (E)nf;
                } else {
                    R NULL;
                }
            }
            else {
                e = (E) a <= -FLT_MAX ? -wf : a >= FLT_MAX ? wf : a;
            }
            ja(&self->x, &e);
            break;
        }
    case KF:{
            F a = PyFloat_AsDouble(arg);

            if (a == -1 && PyErr_Occurred()) {
                if (arg == Py_None) {
                     PyErr_Clear();
                     a = nf;
                } else {
                    R NULL;
                }
            }
            ja(&self->x, &a);
            break;
        }
    case KC:{
            char *a;

            Py_ssize_t n;

            if (-1 == PyString_AsStringAndSize(arg, &a, &n))
                R NULL;

            if (n != 1)
                R PyErr_Format(PyExc_TypeError,
                               "K.ja: a one-, not %zd-character string", n);
            ja(&self->x, a);
            break;
        }
    case KS:{
            char *a;
            Py_ssize_t n;
            if (-1 == PyString_AsStringAndSize(arg, &a, &n))
                R NULL;

            js(&self->x, sn(a, n));
            break;
        }
    case KM:{

        }
    case KD:{

        }
    case KZ:{

        }
    case KU:{

        }
    case KV:{

        }
    case KT:{
            R PyErr_Format(PyExc_NotImplementedError, "appending to type %d",
                           (int)self->x->t);
        }
    }
    Py_RETURN_NONE;
}

static PyObject *
K_jv(KObject * self, KObject * arg)
{
    if (!K_Check(arg))
        R PyErr_Format(PyExc_TypeError, "K._jv: expected K object, not %s",
                       Py_TYPE(arg)->tp_name);
    jv(&self->x, arg->x);
    Py_RETURN_NONE;
}

static K k_repr;

static PyObject *
K_str(KObject * self)
{
    PyObject *res;
    K x = self->x;

    switch (xt) {
    case KC:
        return PY_STR_FromStringAndSize((S) xC, xn);
    case -KS:
        return PY_STR_FromString(xs);
    case -KC:
        return PY_STR_FromStringAndSize((S) & xg, 1);
    case 101:
        if(xj == 0)
            return PY_STR_FromString("::");
    }
    x = k(0, "@", r1(k_repr), r1(x), (K) 0);
    if (xt == -128)
        return PyErr_SetString(ErrorObject, xs ? xs : (S) "not set"), r0(x),
            NULL;
    res = PY_STR_FromStringAndSize((S) xC, xn);
    r0(x);
    return res;
}

static PyObject *
K_repr(KObject * self)
{
    K x = self->x;

    PyObject *f, *s, *r;

    /* special-case :: (issue #663) */
    if (xt == 101 && xj == 0)
        R PY_STR_FromString("k('::')");

    x = k(0, "@", r1(k_repr), r1(x), (K) 0);
    if (xt == -128) {
        r = PY_STR_FromFormat("<k object at %p of type %hd, '%s>",
                              self->x, (H) self->xt, xs);
        R r0(x), r;
    }

    f = PY_STR_FromString("k(%r)");
    if (f == NULL)
        R r0(x), NULL;

    s = PY_STR_FromStringAndSize((S) xC, xn);
    if (s == NULL) {
        Py_DECREF(f);
        R r0(x), NULL;
    }

    r = PY_STR_Format(f, s);
    Py_DECREF(f);
    Py_DECREF(s);
    R r0(x), r;
}

/** Array interface **/

/* Array Interface flags */
#define FORTRAN       0x002
#define ALIGNED       0x100
#define NOTSWAPPED    0x200
#define WRITEABLE     0x400
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

static char typechars[20] = "ObXXuiiiffSOXiifXiii";

static int
k_typekind(K x)
{
    int t = abs(x->t);

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
        1,              /* bool */
#if KXVER>=0
        16,
#else
        0,
#endif
        0, 1,           /* byte */
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
    };
    int t = abs(x->t);

    if (t < sizeof(itemsizes) / sizeof(*itemsizes))
        return itemsizes[t];
    if (t < ENUMS_END)
        return 4;
    return 0;
}

static void
#if PY_MAJOR_VERSION >= 3
k_array_struct_free(PyObject *cap)
{
    void *ptr = PyCapsule_GetPointer(cap, NULL);

    void *arr = PyCapsule_GetContext(cap);
#else
k_array_struct_free(void *ptr, void *arr)
{
#endif
    PyArrayInterface *inter = (PyArrayInterface *) ptr;
    if (inter->shape != NULL)
        free(inter->shape);
    free(inter);
    Py_DECREF((PyObject *)arr);
}

static PyObject *
K_array_struct_get(KObject * self)
{
    K k = self->x;
    PyArrayInterface *inter;
    int typekind, nd;
    typekind = k_typekind(k);

#if PY_MAJOR_VERSION >= 3
        PyErr_SetString(PyExc_AttributeError, "__array_struct__");
        return NULL;
#endif
    if (!k) {
        PyErr_SetString(PyExc_AttributeError, "Null k object");
        return NULL;
    }

    if (strchr("XO", typekind)) {
        PyErr_Format(PyExc_AttributeError, "Unsupported K type %d"
                     " (maps to %c)", k->t, (char)typekind);
        return NULL;
    }
    if (!(inter = (PyArrayInterface *) malloc(sizeof(PyArrayInterface))))
        goto fail_inter;
    nd = (k->t >= 0);       /* scalars have t < 0 in k4 */

    inter->version = 2;
    inter->nd = nd;
    inter->typekind = typekind;
    inter->itemsize = k_itemsize(k);
    inter->flags = ALIGNED | NOTSWAPPED | WRITEABLE;
    if (nd) {
        if (!(inter->shape = (Py_intptr_t *) malloc(sizeof(Py_intptr_t) * 2)))
            goto fail_shape;
        inter->shape[0] = k->n;
        inter->strides = inter->shape + 1;
        inter->strides[0] = inter->itemsize;
        inter->data = kG(k);
    }
    else {
        inter->shape = inter->strides = NULL;
        inter->data = &k->g;
    }
    Py_INCREF(self);
#if PY_MAJOR_VERSION >= 3
    PyObject *cap =
        PyCapsule_New(inter, "__array_struct__", &k_array_struct_free);
    if (PyCapsule_SetContext(cap, self)) {
        Py_DECREF(cap);
        return NULL;
    }
    return cap;
#else
    return PyCObject_FromVoidPtrAndDesc(inter, self, &k_array_struct_free);
#endif
  fail_shape:
    free(inter);
  fail_inter:
    return PyErr_NoMemory();
}

static PyObject *
K_array_typestr_get(KObject * self)
{
    K k = self->x;

    static int const one = 1;

    char const endian = "><"[(int)*(char const *)&one];

    char const typekind = k_typekind(k);

    return PY_STR_FromFormat("%c%c%d", typekind == 'O' ? '|' : endian,
                             typekind, k_itemsize(k));
}

static PyObject *K_K(PyTypeObject * type, PyObject *arg);

static PyObject *
K_call_any(KObject * self, PyObject *args)
{
    PyObject *ret, *kargs;

    switch (PyTuple_GET_SIZE(args)) {
    case 0:
        R K_a0(self);
    case 1:
        R K_a1(self, PyTuple_GET_ITEM(args, 0));
    }
    kargs = K_K(Py_TYPE(self), args);
    if (kargs == NULL)
        R NULL;

    ret = K_dot(self, kargs);
    Py_DECREF(kargs);
    R ret;
}

# define K_call K_call_any

static PyObject*
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
        char *s, unit;
        Py_ssize_t n;
        PyObject *descr = array_descr(obj);
        if (descr == NULL)
            return -1;
        if (PY_STR_AsStringAndSize(descr, &s, &n) == -1) {
            Py_DECREF(descr);
            return -1;
        }
        if (n < 5) {
            PyErr_Format(PyExc_TypeError, "invalid descr %s", s);
            Py_DECREF(descr);
            return -1;
        }
        unit = s[4];
        Py_DECREF(descr);
        switch(unit) {
        case 'Y':
            *offset = (1970 - 2000) * 12;
            *scale = 12;
            return itemsize == 8 ? KM : -1;
        case 'M':
            *offset = (1970 - 2000) * 12;
            *scale = 1;
            return itemsize == 8 ? KM : -1;
        case 'W':
            *offset = -10957;
            *scale = 7;
            return itemsize == 8 ? KD : -1;
        case 'D':
            *offset = -10957;
            *scale = 1;
            return itemsize == 8 ? KD : -1;
        default:
            PyErr_Format(PyExc_TypeError, "invalid descr %s", s);
            return -1;
        }}
    case 'm': {
        char *s, unit[2];
        Py_ssize_t n;
        PyObject *descr = array_descr(obj);
        if (descr == NULL)
            return -1;
        if (PY_STR_AsStringAndSize(descr, &s, &n) == -1) {
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
        switch(unit[0]) {
            case 's':
	         switch(unit[1]) {
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
        PyErr_SetString(PyExc_NotImplementedError, "typecode 'V' is not implemented in C");
        return -1;
    }}
  error:
    PyErr_Format(PyExc_TypeError, "cannot handle type '%c%d'",
                 inter->typekind, inter->itemsize);
    return -1;
}

/* K class methods */
PyDoc_STRVAR(K_from_array_interface_doc, "K object from __array_struct__");
static PyObject *
K_from_array_interface(PyTypeObject * type, PyObject *args)
{
    PyObject *arg, *obj;
    PyArrayInterface *inter;
    J offset = 0, scale = 1;
    K x;

    int t, s;
    if (!PyArg_ParseTuple(args, "O|O:K._from_array_interface", &arg, &obj))
        return NULL;

#if PY_MAJOR_VERSION >= 3
    if (!PyCapsule_CheckExact(arg)) {
        PyErr_Format(PyExc_ValueError, "invalid __array_struct__ type:"
                     " expected PyCapsule, not %s", Py_TYPE(arg)->tp_name);
        return NULL;
    }
    inter = (PyArrayInterface *) PyCapsule_GetPointer(arg, NULL);
    if (inter == NULL)
        return NULL;
#else
    if (!PyCObject_Check(arg)) {
        PyErr_Format(PyExc_ValueError, "invalid __array_struct__ type:"
                     " expected PyCObject, not %s", Py_TYPE(arg)->tp_name);
        return NULL;
    }
    inter = (PyArrayInterface *) PyCObject_AsVoidPtr(arg);
    if (inter == NULL)
        return NULL;
#endif
    if (inter->version != 2) {
        PyErr_Format(PyExc_ValueError, "invalid __array_struct__:"
                     " expected version 2, not %d", inter->version);
        return NULL;
    }
    if (inter->nd > 1) {
        PyErr_Format(PyExc_ValueError, "cannot handle nd=%d", inter->nd);
        return NULL;
    }
    s = inter->itemsize;
    t = k_ktype(inter, obj, &offset, &scale);
    if (t < 0) {
        return NULL;
    }
    x = inter->nd ? ktn(t, inter->shape[0]) : ka(-t);
    if (!x)
        return PyErr_NoMemory();
    if (xt == -128) {
        PyErr_SetString(ErrorObject, xs);
        return NULL;
    }
    if (t == KS) {
        PyObject **src = (PyObject **)inter->data;

        if (inter->nd) {
            S *dest = xS;

            int n = inter->shape[0], i;

            dest = xS;
            for (i = 0; i < n; ++i) {
                PyObject *obj = src[i * inter->strides[0] / s];

                if (!PY_STR_Check(obj)) {
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
    } else if (t == KD || t == KM) {
        if (inter->nd) {
            DO(inter->shape[0], xI[i] = (I)(offset + scale * *(long long *)((S)inter->data + i * inter->strides[0])));
        }
        else
            xi = (I)(offset + scale * *(long long *)inter->data);
    } else if (t == KN && scale != 1) {
        if (inter->nd) {
            DO(inter->shape[0], xJ[i] = (J)(scale * *(long long *)((S)inter->data + i * inter->strides[0])));
        }
        else
            xj = (J)(scale * *(long long *)inter->data);
    }
    else {
        if (inter->nd) {
            int n = inter->shape[0];

            DO(n, memcpy(xG + i * s, (S)inter->data + i * inter->strides[0], s));
        }
        else
            memcpy(&x->g, inter->data, inter->itemsize);
    }
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_ktd_doc, "flip from keyed table(dict)");
static PyObject *
K_ktd(PyTypeObject * type, PyObject *args)
{
    K x = 0;

    if (!PyArg_ParseTuple(args, "O&", &getK, &x)) {
        return NULL;
    }
    if (!x) {
        PyErr_BadArgument();
        return NULL;
    }
    return KObject_FromK(type, ktd(r1(x)));
}

PyDoc_STRVAR(K_err_doc, "sets a K error\n\n>>> K.err('test')\n");
static PyObject *
K_err(PyTypeObject * type, PyObject *args)
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
Z K di(I d)
{
    PyObject *r;

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
        R krr("py");
    }
    Py_DECREF(r);
    R 0;
}

PyDoc_STRVAR(K_sd0_doc, "stop");
static PyObject *
K_sd0(PyTypeObject * type, PyObject *args)
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
K_sd1(PyTypeObject * type, PyObject *args)
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

    return PyInt_FromLong(xi);
}

PyDoc_STRVAR(K_ka_doc, "returns a K atom");
static PyObject *
K_ka(PyTypeObject * type, PyObject *args)
{
    H t;
    J j;
    K x;

    if (!PyArg_ParseTuple(args, "hL:K._ka", &t, &j))
        return NULL;
    x = ktj(t, j);

    return KObject_FromK(type, x);
}

#define K_ATOM(a, T, t, doc)                                    \
        PyDoc_STRVAR(K_k##a##_doc, doc);                        \
        static PyObject *                                       \
        K_k##a(PyTypeObject *type, PyObject *args)              \
        {                                                       \
                K x;                                            \
                T g;                                            \
                if (!PyArg_ParseTuple(args, #t ":K._k"#a, &g))  \
                        return NULL;                            \
                x = k##a(g);                                    \
                return KObject_FromK(type, x);                  \
        }

K_ATOM(b, G, b, "returns a K bool")
K_ATOM(g, G, b, "returns a K byte")
K_ATOM(h, H, h, "returns a K short")
K_ATOM(i, I, i, "returns a K int")

ZS th(I i)
{
    SW(i) {
    CS(1, R "st") CS(2, R "nd") CS(3, R "rd")};
    R "th";
}

PyDoc_STRVAR(K_B_doc, "returns a K bool list");
static PyObject *
K_B(PyTypeObject * type, PyObject *arg)
{
    PyObject *ret = NULL;
    PyObject *seq = PySequence_Fast(arg, "K._B: not a sequence");
    int i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KB, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (o == Py_False)
            xG[i] = (G) 0;
        else if (o == Py_True)
            xG[i] = (G) 1;
        else {
            r0(x);
            PyErr_Format(PyExc_TypeError,
                         "K._B: %d-%s item is not a bool", i + 1, th(i + 1));
            goto error;
        }
    }
    ret = KObject_FromK(type, x);
  error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_I_doc, "returns a K int list");
static PyObject *
K_I(PyTypeObject * type, PyObject *arg)
{
    PyObject *ret = NULL;

    long item;

    PyObject *seq = PySequence_Fast(arg, "K._I: not a sequence");
    int i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KI, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

#if PY_MAJOR_VERSION < 3
        if (PyInt_Check(o))
            item = PyInt_AS_LONG(o);
        else
#endif
        if (PyLong_Check(o)) {
            item = PyLong_AsLong(o);
            if (item == -1 && PyErr_Occurred()) {
                r0(x);
                goto error;
            }
        }
        else {
            if (o == Py_None)
                item = ni;
            else {
                r0(x);
                PyErr_Format(PyExc_TypeError,
                             "K._I: %d-%s item is not an int", i + 1,
                             th(i + 1));
                goto error;
            }
        }
        if (sizeof(I) != sizeof(long) && item != (I) item) {
            r0(x);
            PyErr_Format(PyExc_OverflowError,
                         "K._I: %d-%s item (%ld) is too big", i + 1, th(i + 1),
                         item);
            goto error;
        }
        xI[i] = (I) item;
    }
    ret = KObject_FromK(type, x);
  error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_J_doc, "returns a K long list");
static PyObject *
K_J(PyTypeObject * type, PyObject *arg)
{
    PyObject *ret = NULL;

    PY_LONG_LONG item;

    PyObject *seq = PySequence_Fast(arg, "K._J: not a sequence");
    int i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KJ, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

#if PY_MAJOR_VERSION < 3
        if (PyInt_Check(o))
            item = PyInt_AS_LONG(o);
        else
#endif
        if (PyLong_Check(o)) {
            item = PyLong_AsLongLong(o);
            if (item == -1 && PyErr_Occurred()) {
                r0(x);
                goto error;
            }
        }
        else {
            if (o == Py_None)
                item = nj;
            else {
                r0(x);
                PyErr_Format(PyExc_TypeError,
                             "K._J: %d-%s item is not an int", i + 1,
                             th(i + 1));
                goto error;
            }
        }
        xJ[i] = item;
    }
    ret = KObject_FromK(type, x);
  error:
    Py_DECREF(seq);
    return ret;
}

K_ATOM(j, J, L, "returns a K long (64 bits)")
K_ATOM(e, E, f, "returns a K real (32 bits)")
K_ATOM(f, F, d, "returns a K float (64 bits)")

PyDoc_STRVAR(K_F_doc, "returns a K float list");
static PyObject *
K_F(PyTypeObject * type, PyObject *arg)
{
    PyObject *seq = PySequence_Fast(arg, "K._F: not a sequence");
    int i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KF, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (!PyFloat_Check(o)) {
            r0(x);
            Py_DECREF(seq);
            PyErr_Format(PyExc_TypeError,
                         "K._F: %d-%s item is not a float", i + 1, th(i + 1));
            return NULL;
        }
        xF[i] = PyFloat_AS_DOUBLE(o);
    }
    Py_DECREF(seq);
    return KObject_FromK(type, x);
}

K_ATOM(c, G, c, "returns a K char")

PyDoc_STRVAR(K_ks_doc, "returns a K symbol");
static PyObject *
K_ks(PyTypeObject * type, PyObject *args)
{
    KObject *ret = 0;
    S s;
    I n;
    K x;

    if (!PyArg_ParseTuple(args, "s#", &s, &n, &K_Type, &ret)) {
        return NULL;
    }
    x = ks(sn(s, n));

    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_kdd_doc, "converts datetime.date to q date");
static PyObject *
K_kdd(PyTypeObject * type, PyDateTime_Date * arg)
{
    int y, m, d;
    K x;
    if (!PyDate_Check(arg))
        return PyErr_Format(PyExc_TypeError, "expected a date object, not %s",
                            Py_TYPE(arg)->tp_name);

    y = PyDateTime_GET_YEAR(arg);
    m = PyDateTime_GET_MONTH(arg);
    d = PyDateTime_GET_DAY(arg);
    x = kd(ymd(y, m, d));

    if (!type) {
        type = &K_Type;
    }
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_D_doc, "returns a K date list");
static PyObject *
K_D(PyTypeObject * type, PyObject *arg)
{
    PyObject *ret = NULL;
    I item;
    int i, n;
    K x;

    PyObject *seq = PySequence_Fast(arg, "K._D: not a sequence");

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KD, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (PyDate_Check(o))
            item =
                ymd(PyDateTime_GET_YEAR(o), PyDateTime_GET_MONTH(o),
                    PyDateTime_GET_DAY(o));
        else if (o == Py_None)
            item = ni;
        else {
            r0(x);
            PyErr_Format(PyExc_TypeError,
                         "K._D: %d-%s item is not a date", i + 1, th(i + 1));
            goto error;
        }
        xI[i] = item;
    }
    ret = KObject_FromK(type, x);
  error:
    Py_DECREF(seq);
    return ret;
}

PyDoc_STRVAR(K_ktt_doc, "converts datetime.time to q time");
static PyObject *
K_ktt(PyTypeObject * type, PyObject *arg)
{
    int h, m, s, u;
    K x;
    if (!PyTime_Check(arg))
        return PyErr_Format(PyExc_TypeError, "expected a time object, not %s",
                            Py_TYPE(arg)->tp_name);

    h = PyDateTime_TIME_GET_HOUR(arg);
    m = PyDateTime_TIME_GET_MINUTE(arg);
    s = PyDateTime_TIME_GET_SECOND(arg);
    u = PyDateTime_TIME_GET_MICROSECOND(arg);
    x = kt(((h * 60 + m) * 60 + s) * 1000 + u / 1000);

    if (!type) {
        type = &K_Type;
    }
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_kzz_doc, "converts datetime.datetime to q datetime");
static PyObject *
K_kzz(PyTypeObject * type, PyObject *arg)
{
    int y, m, d, h, u, s, i;
    K x;
    if (!PyDateTime_Check(arg))
        return PyErr_Format(PyExc_TypeError, "expected a date object, not %s",
                            Py_TYPE(arg)->tp_name);

    y = PyDateTime_GET_YEAR(arg);
    m = PyDateTime_GET_MONTH(arg);
    d = PyDateTime_GET_DAY(arg);
    h = PyDateTime_DATE_GET_HOUR(arg);
    u = PyDateTime_DATE_GET_MINUTE(arg);
    s = PyDateTime_DATE_GET_SECOND(arg);
    i = PyDateTime_DATE_GET_MICROSECOND(arg);
    x = kz(ymd(y, m, d) +
           (((h * 60 + u) * 60 + s) * 1000 +
            i / 1000) / (24 * 60 * 60 * 1000.));
    if (!type) {
        type = &K_Type;
    }
    return KObject_FromK(type, x);
}

#ifdef KN
PyDoc_STRVAR(K_knz_doc, "converts datetime.datetime to q timestamp");
static PyObject *
K_knz(PyTypeObject * type, PyObject *arg)
{
    int d, s, u;
    K x;
    if (!PyDelta_Check(arg))
        return PyErr_Format(PyExc_TypeError,
                            "expected a timedelta object, not %s",
                            Py_TYPE(arg)->tp_name);

    d = ((PyDateTime_Delta *) arg)->days;
    s = ((PyDateTime_Delta *) arg)->seconds;
    u = ((PyDateTime_Delta *) arg)->microseconds;
    x = ktj(-KN, 1000000000ll * (d * 24 * 60 * 60 + s) + 1000l * u);

    if (!type) {
        type = &K_Type;
    }
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_kpz_doc, "converts datetime.timedelta to q timespan");
static PyObject *
K_kpz(PyTypeObject * type, PyObject *arg)
{
    int y, m, d, h, u, s, i;
    K x;
    if (!PyDateTime_Check(arg))
        return PyErr_Format(PyExc_TypeError, "expected a date object, not %s",
                            Py_TYPE(arg)->tp_name);

    y = PyDateTime_GET_YEAR(arg);
    m = PyDateTime_GET_MONTH(arg);
    d = PyDateTime_GET_DAY(arg);
    h = PyDateTime_DATE_GET_HOUR(arg);
    u = PyDateTime_DATE_GET_MINUTE(arg);
    s = PyDateTime_DATE_GET_SECOND(arg);
    i = PyDateTime_DATE_GET_MICROSECOND(arg);
    x = ktj(-KP, 1000000000ll * (((ymd(y, m, d) * 24 + h) * 60 + u) * 60 + s)
              + 1000l * i);

    if (!type) {
        type = &K_Type;
    }
    return KObject_FromK(type, x);
}
#endif
PyDoc_STRVAR(K_S_doc, "returns a K symbol list");
static PyObject *
K_S(PyTypeObject * type, PyObject *arg)
{
    PyObject *seq = PySequence_Fast(arg, "K._S: not a sequence");
    int i, n;
    K x;

    if (seq == NULL)
        return NULL;
    n = PySequence_Fast_GET_SIZE(seq);

    x = ktn(KS, n);

    for (i = 0; i < n; ++i) {
        PyObject *o = PySequence_Fast_GET_ITEM(seq, i);

        if (!PY_STR_Check(o)) {
            r0(x);
            Py_DECREF(seq);
            PyErr_Format(PyExc_TypeError,
                         "K._S: %d-%s item is not a string", i + 1, th(i + 1));
            return NULL;
        }
        PY_SET_SN(xS[i], o)
    }
    Py_DECREF(seq);
    return KObject_FromK(type, x);
}

K_ATOM(m, I, i, "returns a K month")
    K_ATOM(d, I, i, "returns a K date")
    K_ATOM(z, F, d, "returns a K datetime")
    K_ATOM(uu, I, i, "returns a K minute")
    K_ATOM(v, I, i, "returns a K second")
    K_ATOM(t, I, i, "returns a K time")
    PyDoc_STRVAR(K_kp_doc, "returns a K string");
     static PyObject *K_kp(PyTypeObject * type, PyObject *args)
{
    KObject *ret = 0;
    S s;
    I n;
    K x;

    if (!PyArg_ParseTuple(args, "s#", &s, &n, &K_Type, &ret)) {
        return NULL;
    }
    x = kpn(s, n);

    if (!type) {
        type = &K_Type;
    }
    return KObject_FromK(type, x);
}

#if KXVER>=3
PyDoc_STRVAR(K_kguid_doc, "returns a K guid");
static PyObject *
K_kguid(PyTypeObject * type, PyObject *args)
{
    U u;

    PyLongObject *pylong;

    if (!PyArg_ParseTuple(args, "O!:K._kguid", &PyLong_Type, &pylong))
        return NULL;
    if (_PyLong_AsByteArray(pylong, u.g, 16, 0, 0) == -1)
        return NULL;
    if (!type)
        type = &K_Type;
    return KObject_FromK(type, ku(u));
}
#endif

PyDoc_STRVAR(K_K_doc, "returns a K general list");
static PyObject *
K_K(PyTypeObject * type, PyObject *arg)
{
    PyObject *seq = PySequence_Fast(arg, "K._K: not a sequence");
    int i, n;
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
            PyErr_Format(PyExc_TypeError,
                         "K._K: %d-%s item is not a K object", i + 1,
                         th(i + 1));
            return NULL;
        }
        xK[i] = r1(((KObject *) o)->x);
    }
    Py_DECREF(seq);
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_ktn_doc, "returns a K list");
static PyObject *
K_ktn(PyTypeObject * type, PyObject *args)
{
    I t, n;
    K x;

    if (!PyArg_ParseTuple(args, "ii:K._ktn", &t, &n)) {
        return NULL;
    }
    x = ktn(t, n);

    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_xT_doc, "table from dictionary");
static PyObject *
K_xT(PyTypeObject * type, PyObject *args)
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
K_xD(PyTypeObject * type, PyObject *args)
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
K_knk(PyTypeObject * type, PyObject *args)
{
    I n;

    K r;

    switch (PyTuple_Size(args) - 1) {
    case 0:{
            if (!PyArg_ParseTuple(args, "i", &n)) {
                return NULL;
            }
            r = knk(n);
            break;
        }
    case 1:{
            K k1;

            if (!PyArg_ParseTuple(args, "iO&", &n, getK, &k1)) {
                return NULL;
            }
            r = knk(n, r1(k1));
            break;
        }
    case 2:{
            K k1, k2;

            if (!PyArg_ParseTuple(args, "iO&O&", &n, getK, &k1, getK, &k2)) {
                return NULL;
            }
            r = knk(n, r1(k1), r1(k2));
            break;
        }
    case 3:{
            K k1, k2, k3;

            if (!PyArg_ParseTuple(args, "iO&O&O&", &n,
                                  getK, &k1, getK, &k2, getK, &k3)) {
                return NULL;
            }
            r = knk(n, r1(k1), r1(k2), r1(k3));
            break;
        }
    case 4:{
            K k1, k2, k3, k4;

            if (!PyArg_ParseTuple(args, "iO&O&O&O&", &n,
                                  getK, &k1,
                                  getK, &k2, getK, &k3, getK, &k4)) {
                return NULL;
            }
            r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4));
            break;
        }
    case 5:{
            K k1, k2, k3, k4, k5;

            if (!PyArg_ParseTuple(args, "iO&O&O&O&O&", &n,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3, getK, &k4, getK, &k5)) {
                return NULL;
            }
            r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5));
            break;
        }
    case 6:{
            K k1, k2, k3, k4, k5, k6;

            if (!PyArg_ParseTuple(args, "iO&O&O&O&O&O&", &n,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3,
                                  getK, &k4, getK, &k5, getK, &k6)) {
                return NULL;
            }
            r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6));
            break;
        }
    case 7:{
            K k1, k2, k3, k4, k5, k6, k7;

            if (!PyArg_ParseTuple(args, "iO&O&O&O&O&O&O&", &n,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3,
                                  getK, &k4,
                                  getK, &k5, getK, &k6, getK, &k7)) {
                return NULL;
            }
            r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), r1(k7));
            break;
        }
    case 8:{
            K k1, k2, k3, k4, k5, k6, k7, k8;

            if (!PyArg_ParseTuple(args, "iO&O&O&O&O&O&O&O&", &n,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3,
                                  getK, &k4,
                                  getK, &k5,
                                  getK, &k6, getK, &k7, getK, &k8)) {
                return NULL;
            }
            r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), r1(k7),
                    r1(k8));
            break;
        }
    case 9:{
            K k1, k2, k3, k4, k5, k6, k7, k8, k9;

            if (!PyArg_ParseTuple(args, "iO&O&O&O&O&O&O&O&O&", &n,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3,
                                  getK, &k4,
                                  getK, &k5,
                                  getK, &k6,
                                  getK, &k7, getK, &k8, getK, &k9)) {
                return NULL;
            }
            r = knk(n, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), r1(k7),
                    r1(k8), r1(k9));
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
K_k(PyTypeObject * type, PyObject *args)
{
    I c;

    char *m;

    K r;

    switch (PyTuple_Size(args) - 2) {
    case 0:{
            if (!PyArg_ParseTuple(args, "is", &c, &m)) {
                return NULL;
            }
            r = k(c, m, (K) 0);
            break;
        }
    case 1:{
            K k1;

            if (!PyArg_ParseTuple(args, "isO&", &c, &m, getK, &k1)) {
                return NULL;
            }
            r = k(c, m, r1(k1), (K) 0);
            break;
        }
    case 2:{
            K k1, k2;

            if (!PyArg_ParseTuple(args, "isO&O&", &c, &m,
                                  getK, &k1, getK, &k2)) {
                return NULL;
            }
            r = k(c, m, r1(k1), r1(k2), (K) 0);
            break;
        }
    case 3:{
            K k1, k2, k3;

            if (!PyArg_ParseTuple(args, "isO&O&O&", &c, &m,
                                  getK, &k1, getK, &k2, getK, &k3)) {
                return NULL;
            }
            r = k(c, m, r1(k1), r1(k2), r1(k3), (K) 0);
            break;
        }
    case 4:{
            K k1, k2, k3, k4;

            if (!PyArg_ParseTuple(args, "isO&O&O&O&", &c, &m,
                                  getK, &k1,
                                  getK, &k2, getK, &k3, getK, &k4)) {
                return NULL;
            }
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), (K) 0);
            break;
        }
    case 5:{
            K k1, k2, k3, k4, k5;

            if (!PyArg_ParseTuple(args, "isO&O&O&O&O&", &c, &m,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3, getK, &k4, getK, &k5)) {
                return NULL;
            }
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), (K) 0);
            break;
        }
    case 6:{
            K k1, k2, k3, k4, k5, k6;

            if (!PyArg_ParseTuple(args, "isO&O&O&O&O&O&", &c, &m,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3,
                                  getK, &k4, getK, &k5, getK, &k6)) {
                return NULL;
            }
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), (K) 0);
            break;
        }
    case 7:{
            K k1, k2, k3, k4, k5, k6, k7;

            if (!PyArg_ParseTuple(args, "isO&O&O&O&O&O&O&", &c, &m,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3,
                                  getK, &k4,
                                  getK, &k5, getK, &k6, getK, &k7)) {
                return NULL;
            }
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), r1(k7),
                  (K) 0);
            break;
        }
    case 8:{
            K k1, k2, k3, k4, k5, k6, k7, k8;

            if (!PyArg_ParseTuple(args, "isO&O&O&O&O&O&O&O&", &c, &m,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3,
                                  getK, &k4,
                                  getK, &k5,
                                  getK, &k6, getK, &k7, getK, &k8)) {
                return NULL;
            }
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), r1(k7),
                  r1(k8), (K) 0);
            break;
        }
    case 9:{
            K k1, k2, k3, k4, k5, k6, k7, k8, k9;

            if (!PyArg_ParseTuple(args, "isO&O&O&O&O&O&O&O&O&", &c, &m,
                                  getK, &k1,
                                  getK, &k2,
                                  getK, &k3,
                                  getK, &k4,
                                  getK, &k5,
                                  getK, &k6,
                                  getK, &k7, getK, &k8, getK, &k9)) {
                return NULL;
            }
            r = k(c, m, r1(k1), r1(k2), r1(k3), r1(k4), r1(k5), r1(k6), r1(k7),
                  r1(k8), r1(k9), (K) 0);
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
    return KObject_FromK(type, r);
}

PyDoc_STRVAR(K_b9_doc,
             "b9(I, K) -> K byte vector\n\nserialize K object");
static PyObject *
K_b9(PyTypeObject * type, PyObject *args)
{
    I i;

    K x;

    if (!PyArg_ParseTuple(args, "iO&:K._b9", &i, &getK, &x))
        return NULL;
    return KObject_FromK(type, b9(i, x));
}

PyDoc_STRVAR(K_d9_doc, "d9(K) -> K byte vector\n\ndeserialize K object");
static PyObject *
K_d9(PyTypeObject * type, PyObject *args)
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
    K k = ((KObject *) self)->x;
    int i = 0;
    char c;

    if (!k) {
        PyErr_SetString(PyExc_ValueError, "null k object");
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "c|i:inspect", &c, &i))
        return NULL;
    switch (c) {
#if KXVER >=3
    case 'm':
        return PyInt_FromLong(k->m);
    case 'a':
        return PyInt_FromLong(k->a);
    case 'n':
        return PyLong_FromSsize_t(k->n);
#else
    case 'n':
        return PyInt_FromLong(k->n);
#endif
    case 'r':
        return PyInt_FromLong(k->r);
    case 't':
        return PyInt_FromLong(k->t);
    case 'u':
        return PyInt_FromLong(k->u);
        /* atoms */
    case 'g':
        return PyInt_FromLong(k->g);
    case '@':
        return _PyLong_FromByteArray(k->G0, 16, 0, 0);
    case 'h':
        return PyInt_FromLong(k->h);
    case 'i':
        return PyInt_FromLong(k->i);
    case 'j':
        return PyLong_FromLongLong(k->j);
    case 'e':
        return PyFloat_FromDouble(k->e);
    case 'f':
        return PyFloat_FromDouble(k->f);
    case 's':
        return (k->t == -KS ? PY_STR_FromString((char *)k->s)
                : k->t == KC ? PY_STR_FromStringAndSize((char *)kG(k), k->n)
                : k->t == -KC ? PY_STR_FromStringAndSize((char *)&k->g, 1)
                : PY_STR_FromFormat("<%p>", k->s));
    case 'c':
        return PyBytes_FromStringAndSize((char *)&k->g, 1);
    case 'k':
        return (k->t == XT ? KObject_FromK(Py_TYPE(self), r1(k->k))
                : PY_STR_FromFormat("<%p>", k->k));
        /* lists */
    case 'G':
        return PyInt_FromLong(kG(k)[i]);
    case 'H':
        return PyInt_FromLong(kH(k)[i]);
    case 'I':
        return PyInt_FromLong(kI(k)[i]);
    case 'J':
        return PyLong_FromLongLong(kJ(k)[i]);
    case 'E':
        return PyFloat_FromDouble(kE(k)[i]);
    case 'F':
        return PyFloat_FromDouble(kF(k)[i]);
    case 'S':
        return (k->t == KS ? PY_STR_FromString((char *)kS(k)[i])
                : PY_STR_FromFormat("<%p>", kS(k)[i]));
    case 'K':
        return KObject_FromK(Py_TYPE(self), r1(kK(k)[i]));
    }
    return PyErr_Format(PyExc_KeyError, "no such field: '%c'", c);
}

/* Calling Python */
ZK
call_python_object(K type, K func, K x)
{
    I n;
    K *args, r;
    PyObject *pyargs, *res;

    if (type->t != -KJ || func->t != -KJ || xt < 0 || xt >= XT) {
        R krr("type error");
    }
    n = xn;
    r1(x);
    if (xt != 0) {
        x = k(0, "(::),", x, (K) 0);
        args = xK + 1;
    }
    else {
        args = xK;
    }
    pyargs = PyTuple_New(n);

    DO(n, PyTuple_SET_ITEM(pyargs, i,
                           KObject_FromK((PyTypeObject *) type->k,
                                         r1(args[i]))));
    res = PyObject_CallObject((PyObject *)func->k, pyargs);
    Py_DECREF(pyargs);
    r0(x);
    if (!res)
        R krr("error in python");

    r = K_Check(res)
        ? r1(((KObject *) res)->x)
        : krr("py-type error");
    Py_DECREF(res);
    return r;
}


static PyObject *
K_func(PyTypeObject * type, PyObject *func)
{
    K f = dl(call_python_object, 3);
    K kfunc = kj(0);
    K ktype = kj(0);
    K x;

    kfunc->k = (K) func;
    ktype->k = (K) type;
    x = knk(3, f, ktype, kfunc);

    xt = 104;           /* projection */
    return KObject_FromK(type, x);
}

PyDoc_STRVAR(K_id_doc, "x._id() -> id of k object");
static PyObject *
K_id(KObject * self)
{
    return PyLong_FromSsize_t((Py_ssize_t) self->x);
}

PyDoc_STRVAR(K_pys_doc, "x._pys() -> python scalar");
static PyObject *K_pys(KObject * self);


static PyMethodDef K_methods[] = {
    {"_func", (PyCFunction)K_func, METH_O | METH_CLASS, "func"},
    {"_dot", (PyCFunction)K_dot, METH_O, "dot"},
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
    {"_kb", (PyCFunction)K_kb, METH_VARARGS | METH_CLASS, K_kb_doc},
    {"_kg", (PyCFunction)K_kg, METH_VARARGS | METH_CLASS, K_kg_doc},
    {"_kh", (PyCFunction)K_kh, METH_VARARGS | METH_CLASS, K_kh_doc},
    {"_ki", (PyCFunction)K_ki, METH_VARARGS | METH_CLASS, K_ki_doc},
    {"_B", (PyCFunction)K_B, METH_O | METH_CLASS, K_B_doc},
    {"_I", (PyCFunction)K_I, METH_O | METH_CLASS, K_I_doc},
    {"_J", (PyCFunction)K_J, METH_O | METH_CLASS, K_J_doc},
    {"_kj", (PyCFunction)K_kj, METH_VARARGS | METH_CLASS, K_kj_doc},
    {"_ke", (PyCFunction)K_ke, METH_VARARGS | METH_CLASS, K_ke_doc},
    {"_kf", (PyCFunction)K_kf, METH_VARARGS | METH_CLASS, K_kf_doc},
    {"_F", (PyCFunction)K_F, METH_O | METH_CLASS, K_F_doc},
    {"_kc", (PyCFunction)K_kc, METH_VARARGS | METH_CLASS, K_kc_doc},
    {"_ks", (PyCFunction)K_ks, METH_VARARGS | METH_CLASS, K_ks_doc},
    {"_S", (PyCFunction)K_S, METH_O | METH_CLASS, K_S_doc},
    {"_km", (PyCFunction)K_km, METH_VARARGS | METH_CLASS, K_km_doc},
    {"_kd", (PyCFunction)K_kd, METH_VARARGS | METH_CLASS, K_kd_doc},
    {"_kdd", (PyCFunction)K_kdd, METH_O | METH_CLASS, K_kdd_doc},
    {"_D", (PyCFunction)K_D, METH_O | METH_CLASS, K_D_doc},
    {"_kz", (PyCFunction)K_kz, METH_VARARGS | METH_CLASS, K_kz_doc},
    {"_kzz", (PyCFunction)K_kzz, METH_O | METH_CLASS, K_kzz_doc},
#ifdef KN
    {"_knz", (PyCFunction)K_knz, METH_O | METH_CLASS, K_knz_doc},
    {"_kpz", (PyCFunction)K_kpz, METH_O | METH_CLASS, K_kpz_doc},
#endif
    {"_ku", (PyCFunction)K_kuu, METH_VARARGS | METH_CLASS, K_kuu_doc},
#if KXVER>=3
    {"_kguid", (PyCFunction)K_kguid, METH_VARARGS | METH_CLASS, K_kguid_doc},
#endif
    {"_kv", (PyCFunction)K_kv, METH_VARARGS | METH_CLASS, K_kv_doc},
    {"_kt", (PyCFunction)K_kt, METH_VARARGS | METH_CLASS, K_kt_doc},
    {"_ktt", (PyCFunction)K_ktt, METH_O | METH_CLASS, K_ktt_doc},
    {"_kp", (PyCFunction)K_kp, METH_VARARGS | METH_CLASS, K_kp_doc},
    {"_ktn", (PyCFunction)K_ktn, METH_VARARGS | METH_CLASS, K_ktn_doc},
    {"_xT", (PyCFunction)K_xT, METH_VARARGS | METH_CLASS, K_xT_doc},
    {"_xD", (PyCFunction)K_xD, METH_VARARGS | METH_CLASS, K_xD_doc},
    {"_K", (PyCFunction)K_K, METH_O | METH_CLASS, K_K_doc},
    {"_b9", (PyCFunction)K_b9, METH_VARARGS | METH_CLASS, K_b9_doc},
    {"_d9", (PyCFunction)K_d9, METH_VARARGS | METH_CLASS, K_d9_doc},

    {"_from_array_interface", (PyCFunction)K_from_array_interface,
     METH_VARARGS | METH_CLASS, K_from_array_interface_doc},

    {"inspect", (PyCFunction)K_inspect, METH_VARARGS, K_inspect_doc},
    {"_id", (PyCFunction)K_id, METH_NOARGS, K_id_doc},
    {"_pys", (PyCFunction)K_pys, METH_NOARGS, K_pys_doc},
    {NULL, NULL}        /* sentinel */
};

#if SIZEOF_LONG == SIZEOF_INT
#define K_INT_CODE "l"
#define K_LONG_CODE "q"
#elif SIZEOF_LONG == SIZEOF_LONG_LONG
#define K_INT_CODE "i"
#define K_LONG_CODE "l"
#else
#error "Unsupported architecture"
#endif

#if PY_VERSION_HEX >= 0x02060000 && KXVER >= 3
char *
k_format(int t)
{
    static char *fmt[] = { "P", "?", "16B", 0, "B",
        "h", K_INT_CODE, K_LONG_CODE, "f", "d",
        "s", "P", K_LONG_CODE, K_INT_CODE, K_INT_CODE,
        "d", K_LONG_CODE, K_INT_CODE, K_INT_CODE, K_INT_CODE,
    };
    if (t < 20)
        return fmt[t];
    if (t < 97)
        return K_INT_CODE;

    return NULL;
}

#define _N_IS_SHAPE ((KXVER >= 3 && SIZEOF_VOID_P == SIZEOF_LONG_LONG) || \
                     (KXVER < 3 && SIZEOF_VOID_P == SIZEOF_INT))

int
K_buffer_getbuffer(KObject * self, Py_buffer * view, int flags)
{
    K x = self->x;
    int itemsize;

    if (!x) {
        PyErr_SetString(PyExc_ValueError, "Null k object");
        return -1;
    }

    itemsize = k_itemsize(x);
    if (itemsize == 0) {
        PyErr_Format(PyExc_BufferError, "k object of type %dh", xt);
        return -1;
    }

    if (xt > 0) {
        view->ndim = 1;
        view->itemsize = itemsize;
        view->format = (flags & PyBUF_FORMAT) ? k_format(xt) : NULL;
        view->len = itemsize * xn;
#if _N_IS_SHAPE
        view->shape = (Py_ssize_t *)&xn;
#else
#    if PY_MAJOR_VERSION < 3
        view->shape = &view->smalltable[0];
#    else
        view->shape = malloc(sizeof(Py_ssize_t));
#    endif
        view->shape[0] = xn;
#endif
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
#if KXVER >= 3
        if (xt == -UU)
            view->buf = x->G0;
        else
#endif
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
        view->len = m * xn * itemsize;

        view->shape = malloc(2 * sizeof(Py_ssize_t));
        view->shape[0] = xn;
        view->shape[1] = m;

        view->suboffsets = suboffsets;
        view->strides = malloc(2 * sizeof(Py_ssize_t));
        view->strides[0] = sizeof(K);
        view->strides[1] = itemsize;

        view->buf = xG;
    }
    Py_INCREF(self);
    view->obj = (PyObject *)self;
    return 0;           /* 0 - success / -1 - failure */
}

void
K_buffer_releasebuffer(KObject * self, Py_buffer * view)
{
    if (view->ndim > 1) {
        free(view->shape);
        free(view->strides);
    }
    else if (view->ndim == 1 && !_N_IS_SHAPE) {
#if PY_MAJOR_VERSION > 2
        free(view->shape);
#endif
    }
    return;
}
#endif

static Py_ssize_t
klen(K x)
{
    if (xt < 0)
        return 1;
    if (xt < 98)
        return xn;
    switch (xt) {
    case 99:           /* dict */
        if (xx->t == 98)
            x = xx;
        else
            return xx->n;
        /* fall through */
    case 98:           /* flip */
        return kK(kK(x->k)[1])[0]->n;
    }
    return 1;
}

static Py_ssize_t
K_length(KObject * k)
{
    return klen(k->x);
}

static PyObject *getitem(PyTypeObject * ktype, K x, Py_ssize_t i);

static PyObject *
K_item(KObject * k, Py_ssize_t i)
{
    return getitem(Py_TYPE(k), k->x, i);
}

static PySequenceMethods K_as_sequence = {
    (lenfunc) K_length, /* sq_length */
    (binaryfunc) 0,     /* sq_concat */
    (ssizeargfunc) 0,   /* sq_repeat */
    (ssizeargfunc) K_item,
};

#if PY_MAJOR_VERSION < 3
static Py_ssize_t
K_buffer_getsegcount(KObject * self, Py_ssize_t * lenp)
{
    return 1;
}

static Py_ssize_t
K_buffer_getcharbuffer(KObject *self, Py_ssize_t segment, const unsigned char **ptrptr)
{
    K x = self->x;
    if (xt != KC) {
        PyErr_Format(PyExc_TypeError, "Expected char vector, not type %d", (int)xt);
        return -1;
    }
    *ptrptr = xG;
    return xn;
}
#endif


static PyBufferProcs K_as_buffer = {
#if PY_MAJOR_VERSION < 3
    (readbufferproc) 0,
    (writebufferproc) 0,
    (segcountproc) K_buffer_getsegcount,
    (charbufferproc) K_buffer_getcharbuffer,
#endif
#if PY_VERSION_HEX >= 0x02060000 && KXVER >= 3
    (getbufferproc) K_buffer_getbuffer,
    (releasebufferproc) K_buffer_releasebuffer,
#endif
};

static PyGetSetDef K_getset[] = {
    {"__array_struct__", (getter) K_array_struct_get, NULL,
     "Array protocol: struct"},
    {"__array_typestr__", (getter) K_array_typestr_get, NULL,
     "Array protocol: typestr"},
    {NULL, NULL, NULL, NULL},   /* Sentinel */
};

static PyObject *k_iter(KObject * o);

static PyObject *
K_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    K x;
    PyObject *obj;

    if (!PyArg_ParseTuple(args, "O:K", &obj))
        return NULL;

    /* check for singletons first */
    if (obj == Py_None)
        x = ktj(101, 0);  /* (::) */
    else if (obj == Py_False)
        x = kb(0);
    else if (obj == Py_True)
        x = kb(1);
    else if (K_Check(obj)) {
        Py_INCREF(obj);
        return obj;
    }
    else if (PY_STR_Check(obj)) {
        S s;
        PY_SET_SN(s, obj);
        x = ks(s);
    }
    else if (PyFloat_Check(obj))
        x = kf(PyFloat_AS_DOUBLE(obj));
#if PY_MAJOR_VERSION < 3
    else if (PyInt_CheckExact(obj))
        x = kj(PyInt_AS_LONG(obj));
#endif
    else if (PyLong_CheckExact(obj)) {
        J j = PyLong_AsLongLong(obj);
        if (j == -1 && PyErr_Occurred())
            return NULL;
        x = kj(j);
    }
    else if (PyDateTime_Check(obj)) {
        return K_kpz(type, obj);
    }
    else if (PyDelta_Check(obj)) {
        return K_knz(type, obj);
    }
    else if (PyDate_Check(obj)) {
        return K_kdd(type, (PyDateTime_Date *) obj);
    }
    else if (PyTime_Check(obj)) {
        return K_ktt(type, obj);
    }
    else {
        PyErr_SetString(PyExc_NotImplementedError, "nyi");
        return NULL;
    }

    R KObject_FromK(type, x);
}


static PyTypeObject K_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
        XSCAT3("_k", QVER, ".K"),       /*tp_name */
    sizeof(KObject),    /*tp_basicsize */
    0,                  /*tp_itemsize */
    /* methods */
    (destructor) K_dealloc,     /*tp_dealloc */
    0,                  /*tp_print */
    0,                  /*tp_getattr */
    0,                  /*tp_setattr */
    0,                  /*tp_compare */
    (reprfunc) K_repr,  /*tp_repr */
    0,                  /*tp_as_number */
    &K_as_sequence,     /*tp_as_sequence */
    0,                  /*tp_as_mapping */
    0,                  /*tp_hash */
    (ternaryfunc) K_call,       /*tp_call */
    (reprfunc) K_str,   /*tp_str */
    0,                  /*tp_getattro */
    0,                  /*tp_setattro */
    &K_as_buffer,       /*tp_as_buffer */
    Py_TPFLAGS_DEFAULT
#if PY_VERSION_HEX >= 0x02070000 && PY_MAJOR_VERSION < 3
        | Py_TPFLAGS_HAVE_NEWBUFFER
#endif
        | Py_TPFLAGS_BASETYPE,  /*tp_flags */
    0,                  /*tp_doc */
    0,                  /*tp_traverse */
    0,                  /*tp_clear */
    0,                  /*tp_richcompare */
    0,                  /*tp_weaklistoffset */
    (getiterfunc) k_iter,       /*tp_iter */
    0,                  /*tp_iternext */
    K_methods,          /*tp_methods */
    0,                  /*tp_members */
    K_getset,           /*tp_getset */
    0,                  /*tp_base */
    0,                  /*tp_dict */
    0,                  /*tp_descr_get */
    0,                  /*tp_descr_set */
    0,                  /*tp_dictoffset */
    (initproc) 0,       /*tp_init */
    0,                  /*tp_alloc */
    K_new,              /*tp_new */
    0,                  /*tp_free */
    0,                  /*tp_is_gc */
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
    return PyInt_FromLong(khp(h, p));
}
#endif

PyDoc_STRVAR(_k_ymd_doc,
             "ymd(y,m,d) -> q date\n\n>>> ymd(2000, 1, 1)\n0\n");

static PyObject *
_k_ymd(PyObject *self, PyObject *args)
{
    int y, m, d;

    if (!PyArg_ParseTuple(args, "iii:ymd", &y, &m, &d))
        return NULL;
    return PyInt_FromLong(ymd(y, m, d));
}

PyDoc_STRVAR(_k_dj_doc, "dj(j) -> yyyymmdd (as int)\n");
static PyObject *
_k_dj(PyObject *self, PyObject *args)
{
    int j;

    if (!PyArg_ParseTuple(args, "i:dj", &j))
        return NULL;
    return PyInt_FromLong(dj(j));
}

/* List of functions defined in the module */
static PyMethodDef _k_methods[] = {
    {"sd0", (PyCFunction)K_sd0, METH_VARARGS, K_sd0_doc},
    {"sd1", (PyCFunction)K_sd1, METH_VARARGS, K_sd1_doc},
    {"ymd", _k_ymd, METH_VARARGS, _k_ymd_doc},
    {"dj", _k_dj, METH_VARARGS, _k_dj_doc},
    {NULL, NULL}        /* sentinel */
};

/*********************** K Object Iterator **************************/

typedef struct {
    PyObject_HEAD PyTypeObject *ktype;
    K x;
    I i, n;
} kiterobject;

static PyTypeObject KObjectIter_Type;

#define KObjectIter_Check(op) PyObject_TypeCheck(op, &KObjectArrayIter_Type)

static PyObject *
k_iter(KObject * obj)
{
    kiterobject *it;

    K x;

    if (!K_Check(obj)) {
        PyErr_BadInternalCall();
        return NULL;
    }
    x = obj->x;

    if (xt < 0) {
        PyErr_Format(PyExc_TypeError, "iteration over a K scalar, t=%d", (int)xt);
        return NULL;
    }

    it = PyObject_GC_New(kiterobject, &KObjectIter_Type);
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
    PyObject_GC_Track(it);
    return (PyObject *)it;
}

static K d2l, m2l, z2l, t2l, v2l, u2l;

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
m2py(I d)
{
    K x, y;
    PyObject *o;
    switch (d) {
    case -wi:
        R PyDate_FromDate(1, 1, 1);
    case wi:
        R PyDate_FromDate(9999, 12, 1);
    case ni:
        Py_RETURN_NONE;
    }
    y = km(d);
    x = k(0, "@", r1(m2l), y, (K) 0);
    o = PyDate_FromDate(xI[0], xI[1], 1);

    r0(x);
    R o;
}

static PyObject *
z2py(F z)
{
    if (isfinite(z)) {
        K y = kz(z), x = k(0, "@", r1(z2l), y, (K) 0);

        PyObject *o = PyDateTime_FromDateAndTime(xI[0], xI[1], xI[2],
                                                 xI[3], xI[4], xI[5],
                                                 (I)round(fmod((z - floor(z))*8.64e10, 1e6)));
        r0(x);
        R o;
    }
    if (isnan(z))
        Py_RETURN_NONE;
    R z < 0 ? PyDateTime_FromDateAndTime(1, 1, 1, 0, 0, 0, 0)
    : PyDateTime_FromDateAndTime(9999, 12, 31, 23, 59, 59, 999999);
}

static PyObject *
t2py(I t)
{
    K x, y;
    PyObject *o;
    if (t == ni)
        Py_RETURN_NONE;
    y = kt(t);
    x = k(0, "@", r1(t2l), y, (K) 0);
    o = PyTime_FromTime(xI[0], xI[1], xI[2], t % 1000 * 1000);
    r0(x);
    R o;
}

static PyObject *
v2py(I t)
{
    K x, y;
    PyObject *o;
    if (t == ni)
        Py_RETURN_NONE;
    y = kv(t);
    x = k(0, "@", r1(v2l), y, (K) 0);
    o = PyTime_FromTime(xI[0], xI[1], xI[2], 0);
    r0(x);
    R o;
}

static PyObject *
u2py(I t)
{
    K x, y;
    PyObject *o;
    if (t == ni)
        Py_RETURN_NONE;
    y = kuu(t);
    x = k(0, "@", r1(u2l), y, (K) 0);
    o = PyTime_FromTime(xI[0], xI[1], 0, 0);
    r0(x);
    R o;
}

static PyObject *
getitem(PyTypeObject * ktype, K x, Py_ssize_t i)
{
    PyObject *ret = NULL;
    Py_ssize_t n = klen(x);
    if (i < 0)
        i += n;
    if (i >= n || i < 0) {
        PyErr_SetString(PyExc_IndexError, "k index out of range");
        return NULL;
    }
    switch (xt) {
    case KS:           /* most common case: use list(ks) */
        ret = PY_STR_InternFromString(xS[i]);
        break;
    case 0:
        ret = KObject_FromK(ktype, r1(xK[i]));
        break;
#if KXVER>=3
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
        ret = PY_STR_FromStringAndSize((S) & xC[i], 1);
        break;
    case KG:
        ret = PyInt_FromLong(xG[i]);
        break;
    case KH:
        ret =
            xH[i] == nh ? Py_INCREF(Py_None), Py_None : PyInt_FromLong(xH[i]);
        break;
    case KI:
        ret =
            xI[i] == ni ? Py_INCREF(Py_None), Py_None : PyInt_FromLong(xI[i]);
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
        ret =
            xJ[i] == nj ? Py_INCREF(Py_None),
            Py_None : PyLong_FromLongLong(xJ[i]);
        break;
    case KE:
        ret = PyFloat_FromDouble(xE[i]);
        break;
    case KF:
        ret = PyFloat_FromDouble(xF[i]);
        break;
    case XT:
        ret = KObject_FromK(ktype, k(0, "@", r1(x), ki(i), (K) 0));
        break;
    default:
        PyErr_SetString(PyExc_NotImplementedError, "not implemented");
    }
    return ret;
}

static PyObject *
kiter_next(kiterobject * it)
{
    PyObject *ret = NULL;

    K x = it->x;

    I i = it->i, n = it->n;

    if (i < n)
        ret = getitem(it->ktype, x, i);
    it->i++;
    return ret;
}

static void
kiter_dealloc(kiterobject * it)
{
    PyObject_GC_UnTrack(it);
    Py_XDECREF(it->ktype);
    r0(it->x);
    PyObject_GC_Del(it);
}

static int
kiter_traverse(kiterobject * it, visitproc visit, void *arg)
{
    if (it->ktype != NULL)
        return visit((PyObject *)(it->ktype), arg);
    return 0;
}

static PyTypeObject KObjectIter_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
        "kiterator",    /* tp_name */
    sizeof(kiterobject),        /* tp_basicsize */
    0,                  /* tp_itemsize */
    /* methods */
    (destructor) kiter_dealloc, /* tp_dealloc */
    0,                  /* tp_print */
    0,                  /* tp_getattr */
    0,                  /* tp_setattr */
    0,                  /* tp_compare */
    0,                  /* tp_repr */
    0,                  /* tp_as_number */
    0,                  /* tp_as_sequence */
    0,                  /* tp_as_mapping */
    0,                  /* tp_hash */
    0,                  /* tp_call */
    0,                  /* tp_str */
    PyObject_GenericGetAttr,    /* tp_getattro */
    0,                  /* tp_setattro */
    0,                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                  /* tp_doc */
    (traverseproc) kiter_traverse,      /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    PyObject_SelfIter,  /* tp_iter */
    (iternextfunc) kiter_next,  /* tp_iternext */
    0,                  /* tp_methods */
};

static PyObject *
K_pys(KObject * self)
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
        return PY_STR_FromStringAndSize((S) &xg, 1);
    case -KG:
        return PyInt_FromLong(xg);
    case -KH:
        return PyInt_FromLong(xh);
    case -KI:
        return PyInt_FromLong(xi);
    case -KJ:
        return PyLong_FromLongLong(xj);
    case -KE:
        return PyFloat_FromDouble(xe);
    case -KF:
        return PyFloat_FromDouble(xf);
    case -KS:
        return PY_STR_FromString(xs);
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

/* Initialization function for the module */
MOD_INIT(_k)
{
    PyObject *m;

    PyDateTime_IMPORT;
    /* date/time to list translations */
    d2l = k(0, "`year`mm`dd$", (K) 0);
    m2l = k(0, "`year`mm$", (K) 0);
    z2l = k(0, "`year`mm`dd`hh`uu`ss$", (K) 0);
    t2l = k(0, "`hh`mm`ss$", (K) 0);
    v2l = k(0, "`hh`mm`ss$", (K) 0);
    u2l = k(0, "`hh`mm$", (K) 0);
    k_none = k(0, "::", (K) 0);
    k_repr = k(0, "-3!", (K) 0);
    debug = getenv("PYQDBG") != NULL;
    /* Create the module and add the functions */
    MOD_DEF(m, XSCAT("pyq._k", QVER), module_doc, _k_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;

    /* Finalize the type object including setting type of the new type
     * object; doing it here is required for portability to Windows
     * without requiring C++. */
    if (PyType_Ready(&K_Type) < 0)
        return MOD_ERROR_VAL;

    /* Add some symbolic constants to the module */
    if (ErrorObject == NULL) {
        ErrorObject = PyErr_NewException("_k.error", NULL, NULL);
        if (ErrorObject == NULL)
            return MOD_ERROR_VAL;
    }
    Py_INCREF(ErrorObject);
    PyModule_AddObject(m, "error", ErrorObject);

    /* Add K */
    PyModule_AddObject(m, "K", (PyObject *)&K_Type);
    /* vector types */
    PyModule_AddIntMacro(m, KB);
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

    return MOD_SUCCESS_VAL(m);
}
