import sublime
import sublime_plugin
import uuid
import os
import re
from . import json
from collections import OrderedDict
from functools import partial

yyp_file_regex_pattern = "^.*\.yyp$"

class GameMakerNewScriptCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # 
        # Make sure a script can be created properly
        # 
        def show_error():
            sublime.error_message("Please make sure you opened your " + 
                        "GameMaker: Studio 2 project root folder as a Sublime project" + 
                        " and you have created at least one script using GameMaker Studio: 2.")

        # Make sure a project is opened
        if not sublime.active_window().project_data():
            show_error()
            return

        project_path = sublime.active_window().extract_variables()["project_path"]
        script_dir_path = project_path + "/scripts"

        if not os.path.isdir(script_dir_path):
            show_error()
            return

        project_info_path = ""
        for filename in os.listdir(project_path):
            if re.match(yyp_file_regex_pattern, filename):
                project_info_path = project_path + "/" + filename
                break

        if not project_info_path:
            show_error()
            return

        # 
        # Start adding the new script
        # 

        # collect script name
        self.view.window().show_input_panel("Script Name:", "", 
            partial(self.make_script, project_info_path, script_dir_path), None, None)

    def make_script(self, project_info_path, script_dir_path, script_name):
        with open(project_info_path, "r+", encoding="utf-8-sig") as f:
            try:
                # Generate script parameters
                script_key = str(uuid.uuid4())
                script_id = str(uuid.uuid4())
                info = json.load(f, object_pairs_hook=OrderedDict)

                # TODO: check if dir or script exisits already

                # Insert the new script into the project info file
                resource_path = "scripts\\%s\\%s.yy" % (script_name, script_name)
                new_resource_item = OrderedDict(
                    [("Key", script_key),
                     ("Value", OrderedDict(
                            [("id", script_id),
                            ("resourcePath", resource_path),
                            ("resourceType", "GMScript")]
                        ))
                    ])
                info['resources'].insert(0, new_resource_item)
                info['script_order'].append(script_key)
                f.seek(0)
                f.write(json.dumps(info, separators=(',', ': '), indent=4))
                f.truncate()
            
                os.chdir(script_dir_path)
                os.mkdir(script_name)
                os.chdir(script_dir_path + "/" + script_name)

                # Generate script file and open for edit
                with open(script_name + ".gml", "w", encoding="utf-8-sig") as f:
                    window = self.view.window()
                    view = window.open_file(script_dir_path + "/" + 
                        script_name + "/" + script_name + ".gml", sublime.ENCODED_POSITION)
                    window.focus_view(view)

                # Generate and fills the script info file
                with open(script_name + ".yy", "w", encoding="utf-8-sig") as f:
                    info = OrderedDict(
                        [("id", script_key),
                        ("modelName", "GMScript"),
                        ("mvc", "1.0"),
                        ("name", script_name),
                        ("IsCompatibility", False),
                        ("IsDnD", False)
                        ])
                    json.dump(info, f, separators=(',', ': '), indent=4)
            except Exception as e:
                print(e)

