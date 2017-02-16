snippet_head = r"""<snippet>
	<content><![CDATA[
"""

snippet_mid = r"""
]]></content>
	<!-- Optional: Set a tabTrigger to define how to trigger the snippet -->
	<tabTrigger>"""

snippet_tail = r"""</tabTrigger>
	<!-- Optional: Set a scope to limit where the snippet will trigger -->
	<scope>source.gml</scope>
</snippet>"""

out_put_dir = "auto_snippets/"

def make_from_txt():
	with open("gml-functions.txt", 'rb') as f:
		content = f.readlines()

		for index in range(0, len(content) - 1, 3):
			name = content[index].strip()
			param = content[index + 1].strip().split(',')
			if len(param) == 1 and param[0] == 'none':
				param = []
			snippet_body = name + '(' + ", ".join("${%d:%s}" % (i + 1, e) for i, e in enumerate(param)) + ')'
			snippet_all = snippet_head + snippet_body + snippet_mid + name + snippet_tail
			with open(out_put_dir + name + ".sublime-snippet", "wb") as out:
				out.write(snippet_all)

def make_from_json():
	with open("gml-functions.json", 'rb') as f:
		import json
		funcs = json.load(f)
		# print(funcs)

		for func in funcs:
			name = func['name']
			params = func['params']
			returns = func['returns']
			snippet_body = name + '(' + ", ".join("${%d:%s}" % (i + 1, e[0]) \
										for i, e in enumerate(params)) + ')'
			snippet_all = snippet_head + snippet_body + snippet_mid + name + snippet_tail
			with open(out_put_dir + name + ".sublime-snippet", "wb") as out:
				out.write(snippet_all)

make_from_json()
