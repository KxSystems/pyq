\d .pyq
/ Implementation of K shift (<< and >>) operators
xprev_:{$[type y;x xprev y;.z.s[x]each y]}
rshift:{xprev_[y;x]}
lshift:{xprev_[neg y;x]}
rrshift:xprev_
rlshift:{xprev_[neg x;y]}

/ Implementation of K.__sizeof__
/  0 1  2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9
sz:0 1 16 0 1 2 4 8 4 8 1 0 8 4 4 8 8 4 4 4
sz[11]:sp:4+4*.z.o like "?64"  / size of a pointer
sn:8-4*.z.K<3                  / size of a count
sizeof:{8+
  $[0>t:type x;sz neg t;
    0=t;sn+(sp*count x)+sum sizeof each x;
    20>t;sn+sz[t]*count x;
    77>t;sn+4*count x;
    97>t;sn+(8*count x)+sz[t-77]*sum count each x;
    98=t;8+sp+sizeof flip x;
    99=t;8+(2*sp)+sum sizeof each(key;value)@\:x;
    sizeof value x]}

/ Argument names
an:{$[100h~t:type x;(value x)1;  / lambda
      101h~t;enlist`x;           / unary
      102h~t;`x`y;               / binary
      103h~t;enlist`f;           / adverb
      104h~t;(a where n),(count n:nils x)_a:.z.s first v:value x;  / projection
      105h~t;'`nyi;              / composition
      106h~t;.z.s value x;       / f'
      '`type]}
/ Detect nils in projections
nils:{
 r:count[a:1_value x]#0b;
 r[i where 0=value each a i:where 101=type each a]:1b;r}
