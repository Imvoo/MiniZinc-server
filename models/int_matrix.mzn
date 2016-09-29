string: viz_int_matrix_file_path = file_path()++".html";

function string: viz_int_matrix(array [int,int] of var int: t) =
 "%%%mzn-json:"++viz_int_matrix_file_path++"\n[\n" ++
    concat(
    [join(", \n", ["{\"x\": " ++ show(j) ++ ", \"y\": " ++ show(i) ++ ", \"val\": " ++ show(t[i,j]) ++ "}"
         |  i in index_set_1of2(t), j in index_set_2of2(t)])])
    ++"]\n%%%mzn-json-end\n";

    