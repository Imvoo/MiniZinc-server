include "globals.mzn";

var set of 1..2: x;
array[1..2] of var bool: y;

constraint
  x = {1} /\
  forall(i in x)(y[i]);

solve satisfy;

%output [
%  "x = ", show(x), "\n",
%  "y = ", show(y), "\n",
%  ];	