/* -*- mode: c; c-basic-offset: 2 -*- */
#include "k.h"
#include <dlfcn.h> 
ZI (*run)(G*);ZV (*fini)(V);ZV (*init)(V);ZK n;
Z K1(f){fini();R r1(n);}
Z K1(e){P(xt!=KC,krr("type"));
  P(run(xC),krr("python"));R r1(n);}
K1(i){P(xt!=KC||xC[xn-1],krr("type"));
  S er;void*h=dlopen((S)xC,RTLD_NOW|RTLD_GLOBAL);
  er=dlerror();P(!h,krr(er));
  run=dlsym(h,"PyRun_SimpleString");P((er=dlerror()),krr(er));
  init=dlsym(h,"Py_Initialize");P((er=dlerror()),krr(er));
  fini=dlsym(h,"Py_Finalize");P((er=dlerror()),krr(er));
  init();R n=k(0,"{.p.e0:x;.z.exit:y}",dl(e,1),dl(f,1),(K)0);}

