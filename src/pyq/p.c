/* -*- mode: c; c-basic-offset: 2 -*- */
#ifndef _WIN32
#include <dlfcn.h>
typedef void *DL;
#define EXPORT
#else /* WINDOWS */
#include <windows.h>
typedef HMODULE DL;
#define dlopen(path, flags)  LoadLibraryA(path)
static const char *
dlerror()
{
    static char buffer[1024]; 
    DWORD err;
    err = GetLastError();
    if (err) {
        FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, err,
            MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), buffer, 1024, NULL);
        return buffer;
    }
    return NULL;
}
#define dlsym GetProcAddress
#define dlclose FreeLibrary
#define strdup _strdup

#endif /* WINDOWS */

#define DLF(h,v,n) do{S r;v=(v##func)dlsym(h,#n);P(!v,(r=(S)dlerror(),krr(r)));}while(0)
#include <stdlib.h>
#include <string.h>
#include "kx/k.h"

#ifdef PY3K
#include <locale.h>
typedef int (*Py_Mainfunc)(int argc, wchar_t **argv);
typedef wchar_t *(*c2w_func)(char*, size_t *);
static c2w_func c2w;
typedef void (*PyMem_FreeFunc)(void *);
static PyMem_FreeFunc PyMem_Free;
#else
typedef int (*Py_Mainfunc)(int argc, char **argv);
#endif

typedef I (*runfunc)(G*);
typedef V (*finifunc)(V);
typedef V (*initfunc)(V);
typedef V*(*estfunc)(V);
typedef V (*ertfunc)(V*);
typedef V (*eitfunc)(V);
typedef enum {LOCKED, UNLOCKED} STATE;
typedef V (*gsrfunc)(STATE);
typedef STATE (*gsefunc)(V);
/*
PyAPI_FUNC(PyThreadState *) PyEval_SaveThread(void);
PyAPI_FUNC(void) PyEval_RestoreThread(PyThreadState *);
PyAPI_FUNC(void) PyGILState_Release(PyGILState_STATE);
PyAPI_FUNC(PyGILState_STATE) PyGILState_Ensure(void);
*/
Z runfunc run;Z finifunc fini;Z initfunc init;Z eitfunc eit;
Z estfunc est;Z ertfunc ert;Z gsrfunc gsr;Z gsefunc gse;
ZK n;ZV *ts;
Z K1(p_fini){ert(ts);fini();R r1(n);}
Z K1(p_eval){
  I r;STATE s;
  P(xt!=KC||xG[xn-1],krr("type"));
  s=gse();
  r=run(xC);
  gsr(s);
  R r?krr("python"):r1(n);}


static Py_Mainfunc Py_Main;

ZK
py(K f, K x)
{
    char **argv;
    char *p, *buf;
    J argc, m;
    I r;
#ifdef PY3K
    wchar_t **wargv;
    wchar_t **wargv_copy;
    char *oldloc;
#endif
    P(f->t != -KS, krr("f type"));
    P(xt, krr("argv type"));
    m = 0;     /* buf length */
    DO(xn,
       K y;
       P((y = kK(x)[i])->t!=KC, krr((S)"arg type"));
       m += y->n+1);
    argc = xn+1;
    argv = malloc(sizeof(char*) * (size_t)argc);
    P(!argv, krr("memory"));
        buf = malloc((size_t)m);
    P(!buf,(free(argv),krr("memory")));
    argv[0] = f->s;
    p = buf;
    DO(xn,
       K y = kK(x)[i];
       argv[i+1] = memcpy(p, kG(y), (size_t)y->n);
       p += y->n; *p++ = '\0');
    gse();
#ifdef PY3K
    wargv = malloc(sizeof(wchar_t*)*(size_t)(argc+1));
    wargv_copy = malloc(sizeof(wchar_t*)*(size_t)(argc+1));
    oldloc = strdup(setlocale(LC_ALL, NULL));
    setlocale(LC_ALL, "");
    DO(argc,P(!(wargv[i]=c2w(argv[i],NULL)),krr("decode")));
        memcpy(wargv_copy, wargv, sizeof(wchar_t*)*(size_t)argc);
    setlocale(LC_ALL, oldloc);
    free(oldloc);
    wargv[argc] = wargv_copy[argc] = NULL;
    r = Py_Main((int)argc, wargv);
    DO(argc,PyMem_Free(wargv_copy[i]));
    free(wargv_copy);
    free(wargv);
#else
    r = Py_Main((int)argc, argv);
#endif
    free(argv);
    free(buf);
    /* Returning to q after finalizing Python is asking for trouble. */
    exit(r);
    R r1(n);
}

K1(p_init){S er;DL h;
  P(n,r1(n));
  P(xt!=KC||xC[xn-1],krr("type"));
  h=dlopen((S)xC,RTLD_NOW|RTLD_GLOBAL);
  er=(S)dlerror();P(!h,krr(er));
  DLF(h,run,PyRun_SimpleString);
  DLF(h,init,Py_Initialize);
  DLF(h,fini,Py_Finalize);
  DLF(h,est,PyEval_SaveThread);
  DLF(h,ert,PyEval_RestoreThread);
  DLF(h,gse,PyGILState_Ensure);
  DLF(h,gsr,PyGILState_Release);
  DLF(h,eit,PyEval_InitThreads);
  DLF(h,Py_Main,Py_Main);
#ifdef PY3K
    const char *error;
    dlerror();    /* Clear any existing error */
#if PY3K < 35
    c2w = (c2w_func)dlsym(h, "_Py_char2wchar");
#else
    c2w = (c2w_func)dlsym(h, "Py_DecodeLocale");
#endif
    P(!c2w, (error = dlerror(),krr((S)error)));
    dlerror();    /* Clear any existing error */
#if PY3K < 34
    PyMem_Free = (PyMem_FreeFunc)dlsym(h, "PyMem_Free");
#else
    PyMem_Free = (PyMem_FreeFunc)dlsym(h, "PyMem_RawFree");
#endif
    P(!PyMem_Free, (error = dlerror(),krr((S)error)));
#endif
  init();
  eit();
  ts = est();
  R n=k(0,"{.p.e:x;.z.exit:y;.p.py:z}",
        dl(p_eval,1),dl(p_fini,1),dl(py,2),(K)0);}

