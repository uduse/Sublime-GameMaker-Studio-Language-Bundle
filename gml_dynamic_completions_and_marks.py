import sublime
import sublime_plugin
import os
import re

mark_dirs = ["objects", "rooms", "tilesets", "sprites", "shaders", "sounds"]
completion_dirs = ["objects", "scripts", "rooms", "tilesets", "sprites", "shaders", "sounds", "timelines"]

def dynamic_completions(search_dirs):
    completion_list = []
    var_dict = sublime.active_window().extract_variables()

    if 'project_path' in var_dict:
        path = var_dict['project_path']
    elif 'folder' in var_dict:
        path = var_dict['folder']
    else:
        return []

    for entry in os.listdir(path):
        abs_path = os.path.join(path, entry)
        if os.path.isdir(abs_path):
            if entry in search_dirs:
                completion_list.extend(collect_all_names(abs_path))
    return completion_list

def collect_all_names(root):
    for path, _, files in os.walk(root):
        if os.path.isdir(path) and any(re.search("^.*\.(yy|fsh|vsh)$", f) for f in files):
            yield os.path.basename(path)

class GameMakerLanguageCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if view.match_selector(locations[0], "source.gml"):
            return [[c, c] for c in dynamic_completions(completion_dirs)]
        else:
            return []

    def on_modified(self, view):
        if view.match_selector(locations[0], "source.gml"):
            view.run_command("mark_dynamic_names")

class MarkDynamicNames(sublime_plugin.TextCommand):
    def run(self, edit):
        pattern = "(?<![A-Za-z0-9_])" + "|".join(dynamic_completions(mark_dirs)) + "(?![A-Za-z0-9_])"
        matches = self.view.find_all(pattern)
        self.view.add_regions("gml_names", matches, scope="source.gml", 
            flags=sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL | sublime.DRAW_STIPPLED_UNDERLINE)