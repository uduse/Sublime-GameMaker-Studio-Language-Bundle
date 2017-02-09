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

with open("gml-functions.txt", 'rb') as f:
	content = f.readlines()

	for index in range(0, len(content) - 1, 3):
		name = content[index].strip()
		param = content[index + 1].strip().split(',')
		if len(param) == 1 and param[0] == 'none':
			param = []
		snippet_body = name + '(' + ", ".join("${%d:%s}" % (i + 1, e) for i, e in enumerate(param)) + ')'
		snippet_all = snippet_head + snippet_body + snippet_mid + name + snippet_tail
		with open("snippets/" + name + ".sublime-snippet", "wb") as out:
			out.write(snippet_all)