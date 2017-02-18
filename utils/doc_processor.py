from collections import namedtuple
from enum import Enum
from collections import OrderedDict

folder_path = "../GameMaker Studio 2 Offical Docs/"
syntax_output_path = "../gml.YAML-tmLanguage"
syntax_output_path_legacy = "../gmll.YAML-tmLanguage"
completions_output_path = "../gml.sublime-completions"
completions_output_path_legacy = "../gmll.sublime-completions"
file_functions = "fnames"
file_functions_legacy = "fnames14"  # Old version of GML

file_keywords = "keywords_gml.txt"

# Future Uses
# file_shader_glsl_functions = "glsl_names"
# file_shader_glsl_keywords = "keywords_glsl.txt"
# file_shader_hlsl_functions = "hlsl_names"
# file_shader_hlsl_keywords = "keywords_hlsl.txt"

Entry = namedtuple("Entry", ["name", "type", "param", "readonly",
                             "spelling", "disallowed", "obsolete"])


# = constant
# * = readonly
# @ = instance variable
# & = obsolete
# $ = US spelling
# £ = UK spelling
# ! = disallowed in free

## Read Functions
def read_functions(path):
    entries = []
    with open(path, "r", encoding='utf-8-sig') as f:
        for line in f:
            if line.strip() and line[:2] != "//":
                name = line.split("(")[0].split("[")[0].strip("#*@&$\n£ ")
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
    return entries


entries = read_functions(folder_path + file_functions)
entries_legacy = read_functions(folder_path + file_functions_legacy)

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

syntax_head_legacy = r"""# [PackageDev] target_format: plist, ext: tmLanguage
---
name: GML
scopeName: source.gmll
fileTypes: [gmll]
uuid: d5149cef-5886-44d8-8940-86eaa7123084

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

completion_head_legacy = r"""{
   "scope": "source.gmll",

   "completions":
   [
"""

completion_tail = r"""
    ]
}"""

completion_output = completion_head
completion_output_legacy = completion_head_legacy

regex_head = "(?<![A-Za-z0-9_])("
regex_tail = ")(?![A-Za-z0-9_])"
patterns = []

syntax_output = syntax_head
syntax_output_legacy = syntax_head_legacy


# Make keywords
def process_keywords(syntax_output, ext):
    syntax_output += syntax_comment + "Keywords" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(keywords) + regex_tail + "\n"
    syntax_output += syntax_name + "keyword." + ext + "\n\n"
    return syntax_output


syntax_output = process_keywords(syntax_output, 'gml')
syntax_output_legacy = process_keywords(syntax_output_legacy, 'gmll')
completion_output += "\t\t" + ",\n\t\t".join("\"%s\"" % keyword for keyword in keywords if len(keyword) > 3) + ",\n\t\t"
completion_output_legacy += "\t\t" + ",\n\t\t".join(
    "\"%s\"" % keyword for keyword in keywords if len(keyword) > 3) + ",\n\t\t"


def process_functions(entries, syntax_output, ext):
    func_names = [entry.name for entry in entries if entry.type == 'func']
    syntax_output += syntax_comment + "Functions" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(func_names) + regex_tail + "\n"
    syntax_output += syntax_name + "support.function." + ext + "\n\n"
    func_completions = []
    for entry in entries:
        if entry.type == 'func':
            params = ", ".join("${%d:%s}" % (i + 1, e) for i, e in enumerate(entry.param))
            completion = "{\"trigger\": \"%s\", \"contents\": \"%s(%s)\"}" % (entry.name, entry.name, params)
            func_completions.append(completion)
    return func_completions, syntax_output


# Make functions
completions, syntax_output = process_functions(entries, syntax_output, 'gml')
completions_legacy, syntax_output_legacy = process_functions(entries_legacy,
                                                             syntax_output_legacy, 'gmll')

completion_output += ",\n\t\t".join(completions) + ",\n\t\t"
completion_output_legacy += ",\n\t\t".join(completions_legacy) + ",\n\t\t"


# Make global vars
def process_global_vars(entries, syntax_output, ext):
    var_names = [entry.name for entry in entries if entry.type == 'glob var']
    syntax_output += syntax_comment + "Global Variables" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
    syntax_output += syntax_name + "variable.language." + ext + "\n\n"
    return var_names, syntax_output


var_names, syntax_output = process_global_vars(entries, syntax_output, "gml")
var_names_legacy, syntax_output_legacy = process_global_vars(entries_legacy, syntax_output_legacy, "gmll")
completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3) + ",\n\t\t"
completion_output_legacy += ",\n\t\t".join("\"%s\"" % var for var in var_names_legacy if len(var) > 3) + ",\n\t\t"


# Make instance vars
def process_instance_var(entries, syntax_output, ext):
    var_names = [entry.name for entry in entries if entry.type == 'inst var']
    syntax_output += syntax_comment + "Instance Variables" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
    syntax_output += syntax_name + "variable.parameter." + ext + "\n\n"
    return var_names, syntax_output


var_names, syntax_output = process_instance_var(entries, syntax_output, "gml")
var_names_legacy, syntax_output_legacy = process_instance_var(entries_legacy, syntax_output_legacy, "gmll")
completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3) + ",\n\t\t"
completion_output_legacy += ",\n\t\t".join("\"%s\"" % var for var in var_names_legacy if len(var) > 3) + ",\n\t\t"


# # Make constants
def process_constants(entries, syntax_output, ext):
    var_names = [entry.name for entry in entries if entry.type == 'const']
    syntax_output += syntax_comment + "Constants" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
    syntax_output += syntax_name + "constant.language." + ext + "\n\n"
    return var_names, syntax_output


var_names, syntax_output = process_constants(entries, syntax_output, "gml")
var_names_legacy, syntax_output_legacy = process_constants(entries_legacy, syntax_output_legacy, "gmll")
completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3)
completion_output_legacy += ",\n\t\t".join("\"%s\"" % var for var in var_names_legacy if len(var) > 3)

# Make other static stuff
syntax_tail = r"""- comment: Line-comments
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
syntax_output += syntax_tail
syntax_output_legacy += syntax_tail

completion_output += completion_tail
completion_output_legacy += completion_tail

# Dump the files
with open(syntax_output_path, 'w', encoding='utf-8') as f:
    f.write(syntax_output)
with open(syntax_output_path_legacy, 'w', encoding='utf-8') as f:
    f.write(syntax_output_legacy)
with open(completions_output_path, 'w', encoding='utf-8') as f:
    f.write(completion_output)
with open(completions_output_path_legacy, 'w', encoding='utf-8') as f:
    f.write(completion_output_legacy)
