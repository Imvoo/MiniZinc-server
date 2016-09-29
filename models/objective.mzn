string: viz_objective_file_path = file_path()++".html";

function string: viz_objective(var int: x) =
  "%%%mzn-json:"++viz_objective_file_path++"\n" ++
  show(x)++"\n%%%mzn-json-time\n"++
  "%%%mzn-json-end\n";