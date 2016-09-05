include "globals.mzn";

int: m;
int: n = m*m;

array[1..m] of var 0..n: mark;

array[1..(m*(m-1)) div 2] of var 0..n: differences =
    [ mark[j] - mark[i] | i in 1..m, j in i+1..m];

constraint mark[1] = 0;

constraint forall ( i in 1..m-1 ) ( mark[i] < mark[i+1] );

constraint alldifferent(differences);

    % Symmetry breaking
constraint differences[1] < differences[(m*(m-1)) div 2];

solve :: int_search(mark, input_order, indomain, complete)
    minimize mark[m];

%output [show(mark)];