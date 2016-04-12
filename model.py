example = {
    'banner' : {
        'hide' : "document.getElementById(\"banner\").style.display='none';",
        'show' : ""
    },
    'table': {
        'hide': "document.getElementById(\"table\").style.display='none';",
        'show': ""
    }
}
def assemble_js_for_code(project, code):
    """ Gets the js-code for a certain project/code combination"""
    global models

    if project in models:
        js = []
        project = models[project]
        rules = sorted(project.keys())
        rule_indexes = [int(c) for c in code.split("-")]

        for i,ri in enumerate(rule_indexes):
            rule = project[rules[i]]

            options = sorted(rule.keys())
            if ri >= 0 and ri < len(options):
                js.append(rule[options[ri]])
        return "".join(js)

    return ""

def search_space():
    pass

models = {
    'example' : example
}