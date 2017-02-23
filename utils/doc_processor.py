# coding=utf-8
from collections import namedtuple

docs_folder_path = "../GameMaker Studio 2 Offical Docs/"
syntax_output_path = "../gml.YAML-tmLanguage"
syntax_output_path_legacy = "../gmll.YAML-tmLanguage"
completions_output_path = "../gml.sublime-completions"
completions_output_path_legacy = "../gmll.sublime-completions"
functions_file_name = "fnames"
functions_file_name_legacy = "fnames14"  # Old version of GML

file_keywords = "keywords_gml.txt"

# For Future Uses
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

def process_documentation(function_path, ext):
    # Read Functions
    entries = read_functions(function_path)
    keywords = read_keywords()

    if ext == "gml":
        name = "GameMaker Language (GML)"
        id = "7eb40f01-b63d-4115-81c7-069f032bb76a"
    else:
        name = "GameMaker Language Legacy (GMLL)"
        id = "44f1359e-0eb0-4662-a52d-bf0c8a454f23"
    syntax_head = r"""# [PackageDev] target_format: plist, ext: tmLanguage
---
name: """ + name + """
scopeName: source.""" + ext + r"""
fileTypes: [""" + ext + r"""]
uuid: """ + id + r"""

patterns:
"""

    syntax_comment = "- comment: "
    syntax_match = "  match: "
    syntax_name = "  name: "

    completion_head = r"""{
    "scope": "source.""" + ext + r"""",

    "completions":
    [
"""

    completion_tail = r"""
        ]
    }"""

    completion_output = completion_head

    regex_head = "(?<![A-Za-z0-9_])("
    regex_tail = ")(?![A-Za-z0-9_])"

    syntax_output = syntax_head

    syntax_output += syntax_comment + "Keywords" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(keywords) + regex_tail + "\n"
    syntax_output += syntax_name + "keyword." + ext + "\n\n"

    completion_output += "\t\t" + ",\n\t\t".join(
        "\"%s\"" % keyword for keyword in keywords if len(keyword) > 3) + ",\n\t\t"

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

    # Make functions
    completion_output += ",\n\t\t".join(func_completions) + ",\n\t\t"

    # Make global vars
    var_names = [entry.name for entry in entries if entry.type == 'glob var']
    syntax_output += syntax_comment + "Global Variables" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
    syntax_output += syntax_name + "variable.language." + ext + "\n\n"
    completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3) + ",\n\t\t"

    # Make instance vars
    var_names = [entry.name for entry in entries if entry.type == 'inst var']
    syntax_output += syntax_comment + "Instance Variables" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
    syntax_output += syntax_name + "variable.parameter." + ext + "\n\n"
    completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3) + ",\n\t\t"

    # # Make constants
    var_names = [entry.name for entry in entries if entry.type == 'const']
    syntax_output += syntax_comment + "Constants" + '\n'
    syntax_output += syntax_match + regex_head + "|".join(var_names) + regex_tail + "\n"
    syntax_output += syntax_name + "constant.language." + ext + "\n\n"
    completion_output += ",\n\t\t".join("\"%s\"" % var for var in var_names if len(var) > 3)

    # Make other static stuff
    syntax_tail = r"""- comment: Line-comments
  match: //[^\n]*
  name: comment.line.""" + ext + r"""

- comment: Block-comments
  begin: /\*
  captures:
    '0':
      name: punctuation.definition.comment.mn
  end: \*/
  name: comment.block.""" + ext + r"""

- comment: Literal, string, double-quoted
  match: '["][^"]*["]'
  name: string.quoted.double.""" + ext + r"""

- comment: Literal, number
  match: '\b[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b'
  name: constant.numeric.""" + ext + r"""
...
"""
    syntax_output += syntax_tail
    completion_output += completion_tail
    return syntax_output, completion_output


def read_keywords():
    keywords = []
    with open(docs_folder_path + file_keywords, "r", encoding='utf-8-sig') as f:
        for line in f:
            if line.strip():
                keywords.append(line.strip())
    return keywords


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


# # Dump the files
syntax, completion = process_documentation(docs_folder_path + functions_file_name, 'gml')
syntax_legacy, completion_legacy = process_documentation(docs_folder_path + functions_file_name_legacy, 'gmll')

with open(syntax_output_path, 'w', encoding='utf-8') as f:
    f.write(syntax)
with open(syntax_output_path_legacy, 'w', encoding='utf-8') as f:
    f.write(syntax_legacy)
with open(completions_output_path, 'w', encoding='utf-8') as f:
    f.write(completion)
with open(completions_output_path_legacy, 'w', encoding='utf-8') as f:
    f.write(completion_legacy)
