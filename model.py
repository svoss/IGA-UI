import pytz

example = {
    'banner': {
        'hide': "document.getElementById(\"banner\").style.display='none';",
        'show': ""
    },
    'table': {
        'hide': "document.getElementById(\"table\").style.display='none';",
        'show': ""
    },
    'colored-text': {
        'black': "",
        'purple': "document.getElementById(\"colored-text\").style.color='purple';",
        'red': "document.getElementById(\"colored-text\").style.color='red';",
        'green': "document.getElementById(\"colored-text\").style.color='green';"
    }
}

models = {
    'example': example
}

settings = {
    'example': {
        'start_code': "0-0-0",
        'evaluation_time_per_individual': .5,  # time need per individual to determine fitness in days
        'population_size': 2,
        'ga_account': '76516435',
        'ga_property': 'UA-76516435-2',
        'ga_profile': '120409781',
        'time_zone': pytz.timezone('Europe/Amsterdam'),
        'prefix': '/example/',
        's3_bucket': 'iga-example-stijnvoss2',
        's3_region': 'us-east-1',
    },
    'FV': {
        'start_code': "0-0-0",
        'evaluation_time_per_individual': .2,  # time need per individual to determine fitness in days
        'population_size': 5,
        'time_zone': pytz.timezone('Europe/Amsterdam'),
        's3_bucket':'',
        's3_region':'',
    }
}


def assemble_js_for_code(project, code):
    """ Gets the js-code for a certain project/individual combination

    :param project:
    :param code:
    """
    global models

    if project in models:
        js = []
        project = models[project]
        rules = sorted(project.keys())
        rule_indexes = [int(c) for c in code.split("-")]

        for i, ri in enumerate(rule_indexes):
            rule = project[rules[i]]

            options = sorted(rule.keys())
            if 0 <= ri < len(options):
                js.append(rule[options[ri]])
        return "".join(js)

    return ""


def search_space(project):
    """ Gets search space for a certain project, as list of variables with possible values

    :param project:
    """
    space = {}
    if project in models:
        project = models[project]
        space = dict([(name, range(0, len(variables.keys()))) for name, variables in project.iteritems()])

    return space


def project_setting(project, setting):
    global settings
    if project not in settings:
        raise Exception("Project %s not in settings" % project)
    project_settings = settings[project]
    if setting not in project_settings:
        raise Exception("Setting %s not in project settings" % setting)

    return project_settings[setting]
