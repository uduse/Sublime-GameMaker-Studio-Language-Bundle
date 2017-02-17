from collections import namedtuple
from enum import Enum
from collections import OrderedDict

folder_path = "../GameMaker Studio 2 Offical Docs/"
syntax_output_path = "../gml.YAML-tmLanguage"
completions_output_path = "../gml.sublime-completions"

file_functions = "fnames"
file_keywords = "keywords_gml.txt"

# Future Uses
# file_function_names_old = "fnames14" # Old version of GML
# file_shader_glsl_functions = "glsl_names"
# file_shader_glsl_keywords = "keywords_glsl.txt"
# file_shader_hlsl_functions = "hlsl_names"
# file_shader_hlsl_keywords = "keywords_hlsl.txt"

Entry = namedtuple("Entry", ["name", "type", "param", "readonly",
                             "spelling", "disallowed", "obsolete"])
entries = []

# = constant
# * = readonly
# @ = instance variable
# & = obsolete
# $ = US spelling
# £ = UK spelling
# ! = disallowed in free


## Read Functions
with open(folder_path + file_functions, "r", encoding='utf-8') as f:
    for line in f:
        if line.strip() and line[:2] != "//":
 
            name = line.split("(")[0].strip("#*@&$\n£")
            param = None

            if "(" in line:
                typ = "func"
                param = [p.strip(")\n ") for p in line.split("(")[1].split(",")]
            elif "#" in line:
                typ = "const"
            elif "@" in line:
                typ = "inst var"
            else:
                typ = "glob var"

            if "$" in line:
                spelling = "US"
            elif "£" in line:
                spelling = "UK"
            else:
                spelling = None

            readonly = "*" in line
            disallowed = "!" in line
            obsolete = "&" in line

            entry = Entry(name=name, type=typ, param=param, readonly=readonly,
                          spelling=spelling, disallowed=disallowed, obsolete=obsolete)
            entries.append(entry)

## Read keywords
keywords = []
with open(folder_path + file_keywords, "r", encoding='utf-8-sig') as f:
    for line in f:
        if line.strip() and "#" not in line:
            keywords.append(line.strip())

syntax_head = r"""# [PackageDev] target_format: plist, ext: tmLanguage
---
name: GML
scopeName: source.gml
fileTypes: [gml]
uuid: 44f1359e-0eb0-4662-a52d-bf0c8a454f23

patterns:
"""

syntax_comment = "- comment: "
syntax_match = "  match: "
syntax_name = "  name: "

completion_head = r"""{
   "scope": "source.gml",

   "completions":
   [
"""

completion_tail = r"""
    ]
}"""

completion_output = completion_head

regex_head = "(?<![A-Za-z0-9_])("
regex_tail = ")(?![A-Za-z0-9_])"
patterns = []

syntax_output = syntax_head

# Make keywords
syntax_output += syntax_comment + "Keywords" + '\n'
syntax_output += syntax_match + regex_head + "|".join(keywords) + regex_tail + "\n"
syntax_output += syntax_name + "keyword.gml" + "\n\n"
completion_output += "\t\t" + ",\n\t\t".join("\"%s\"" % keyword for keyword in keywords if len(keyword) > 3) + ",\n\t\t"

# Make functions
func_names = [entry.name for entry in entries if entry.type == 'func']
syntax_output += syntax_comment + "Functions" + '\n'
syntax_output += syntax_match + regex_head + "|".join(func_names) + regex_tail + "\n"
syntax_output += syntax_name + "support.function.gml" + "\n\n"
func_completions = []
for entry in entries:
    if entry.type == 'func':
        params = ", ".join("${%d:%s}" % (i + 1, e) for i, e in enumerate(entry.param))
        completion = "{\"trigger\": \"%s\", \"contents\": \"%s(%s)\"}" % (entry.name, entry.name, params)
        func_completions.append(completion)
completion_output += ",\n\t\t".join(func_completions) + ",\n\t\t"

# Make global vars
var_names = [entry.name for entry in entries if entry.type == 'glob var']
syntax_output += syntax_comment + "Global Variables" + '\n'
syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
syntax_output += syntax_name + "variable.language.gml" + "\n\n"
completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3) + ",\n\t\t"

# Make instance vars
var_names = [entry.name for entry in entries if entry.type == 'inst var']
syntax_output += syntax_comment + "Instance Variables" + '\n'
syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
syntax_output += syntax_name + "variable.parameter.gml" + "\n\n"
completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3) + ",\n\t\t"

# # Make constants
var_names = [entry.name for entry in entries if entry.type == 'const']
syntax_output += syntax_comment + "Constants" + '\n'
syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
syntax_output += syntax_name + "constant.language.gml" + "\n\n"
completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3)

# Make other static stuff
syntax_output += r"""- comment: Line-comments
  match: //[^\n]*
  name: comment.line.gml

- comment: Block-comments
  begin: /\*
  captures:
    '0':
      name: punctuation.definition.comment.mn
  end: \*/
  name: comment.block.gml

- comment: Literal, string, double-quoted
  match: '["][^"]*["]'
  name: string.quoted.double.gml

- comment: Literal, number
  match: '\b[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b'
  name: constant.numeric.gml
...
"""

completion_output += completion_tail

# Dump the files
with open(syntax_output_path, 'w', encoding='utf-8') as f:
    f.write(syntax_output)
with open(completions_output_path, 'w', encoding='utf-8') as f:
    f.write(completion_output)
