source .venv/bin/activate

export edarw_source_path=${PWD}
export edarw_examples_path=${edarw_source_path}/examples

append_to_python_path_if_not ${edarw_source_path}/src
append_to_python_path_if_not ${edarw_source_path}/tools
append_to_python_path_if_not ${edarw_source_path}/src/edarw

# PYTHONPYCACHEPREFIX
#   If this is set, Python will write .pyc files in a mirror directory tree at this path,
#   instead of in __pycache__ directories within the source tree.
#   This is equivalent to specifying the -X pycache_prefix=PATH option.
export PYTHONPYCACHEPREFIX=$PWD/.pycache
