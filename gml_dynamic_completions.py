import sublime
import sublime_plugin
import os
import re

class GameMakerLanguageCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.gml"):
            return []
        else:
            return [[c, c] for c in self.dynamic_completions()]

    def dynamic_completions():
        completion_list = []
        project_path = sublime.active_window().extract_variables()['project_path']
        for entry in os.listdir(project_path):
            abs_path = os.path.join(project_path, entry)
            if os.path.isdir(abs_path):
                if entry in ["objects", "scripts", "rooms", "tilesets"]:
                    completion_list.extend(self.collect_all_names(abs_path))
        return completion_list

    def collect_all_names(self, root):
        for path, _, files in os.walk(root):
            if os.path.isdir(path) and any(re.search("^.*\.yy$", f) for f in files):
                yield os.path.basename(path)

