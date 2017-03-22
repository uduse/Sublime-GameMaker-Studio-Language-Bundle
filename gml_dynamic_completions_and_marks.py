import sublime
import sublime_plugin
import os
import re
import json

yy_file_regex_pattern = "^.*\.yy$"

def parse_yy_file(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        try:
            data = json.load(f)
            model = data['modelName'][2:]
            name = data['name']
            if model == "Room":
                for layer in data['layers']:
                    yield ("Layer", layer['name'])
            yield (model, name)
        except Exception as e:
            pass

def generate_completions(exclude_folders=["views"]):
    folders = sublime.active_window().folders()
    completions = []
    for folder in folders:
        for path, _, files in os.walk(folder):
            if os.path.basename(path) not in exclude_folders:
                for file in files:
                    if re.search(yy_file_regex_pattern, file):
                        completions.extend(parse_yy_file(os.path.join(path, file)))
    return completions

class GameMakerLanguageCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if view.match_selector(locations[0], "source.gml"):
            return [["%s\t〔%s〕" % (name, model), name] for model, name in generate_completions()]

    # def on_modified(self, view):
    #     if re.search(".*\.gml", view.file_name()):
    #         view.run_command("mark_dynamic_names")

# class MarkDynamicNames(sublime_plugin.TextCommand):
#     def run(self, edit):
#         names = [name for _, name in generate_completions(["views", "scripts"])]
#         print(names)
#         pattern = "(?<![A-Za-z0-9_])" + "|".join(names) + "(?![A-Za-z0-9_])"
#         matches = self.view.find_all(pattern)
#         self.view.add_regions("gml_names", matches, scope="source.gml",
#                               flags=sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL | sublime.DRAW_STIPPLED_UNDERLINE)