import pytz

FV = {
    'labels': {
        'normal': '',
        'red': 'var labels=document.getElementsByClassName("labels"); for(var i =1; i < labels.length; i++){var s = labels[i].style; s.color="white"; s.background="#e51709"; s.textShadow:"none";} ',
        'green': 'var labels=document.getElementsByClassName("labels"); for(var i =1; i < labels.length; i++){var s = labels[i].style; s.color="white"; s.background="#0dbd16"; s.textShadow:"none";}',
        'grey':'var labels=document.getElementsByClassName("labels"); for(var i =1; i < labels.length; i++){var s = labels[i].style; s.color="white"; s.background="#999999"; s.textShadow:"none";}'
    },
    'genres': {
        'normal': '',
        'red': "$('li.genrelinks a').css('background','#e51709').css('color','white').css('textShadow','none');",
        'green': "$('li.genrelinks a').css('background','#0dbd16').css('color','white').css('textShadow','none');",
        'grey': "$('li.genrelinks a').css('background','#999999').css('color','white').css('textShadow','none');"
    },
    'comparable_blocks': {
        'normal': '',
        # ff checken of er nog iets aan de de lazyload gedaan kan worden..
        'up': "$('div.filmpagina-info').after($('div.filmpagina-vergelijkbaar-container'));"
    },
    'actors_block': {
        'normal': '',
        'up': "$('li.genrelinks').after($('strong:contains(\"Acteurs\")').parent())"
    },
    'filmpagina-knop': {
        'normal':'',
        'larger':"$('.filmpagina-knop').css('font-size','13px');",
        'green':"$('.filmpagina-knop').css('background','#0dbd16').css('textShadow','none').css('border','none').css('box-shadow','none').css('font-size','13px');"
    },
    'watchlist': {
        'normal': '',
        'up':"$('div.filmpagina-info-cover div.img').before($('div.filmpagina-info-cover div.watchlist')[0]);"
    },
    'tabs-positioning-3':{
        'normal':'',
        'netflix':"$('li.filmpagina-tabs-netflix').insertAfter($('li.filmpagina-tabs-cast'));",
        'kopen':"$('li.filmpagina-tabs-kopen').insertAfter($('li.filmpagina-tabs-cast'));",
        'tv-gemist':"$('li.filmpagina-tabs-eerderoptv').insertAfter($('li.filmpagina-tabs-cast'));"

    },
    'netflix':{
        'normal':'',
        'red':"$('li.filmpagina-tabs-netflix a').css('background-color','#e51709');"
    }
}

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
    'example': example,
    'FV': FV
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
        'example_url':'http://iga.stijnvoss.com/',
        's3_bucket': 'iga-example-stijnvoss2',
        's3_region': 'us-east-1',
    },
    'FV': {
        'start_code': "0-0-2-2-2-0-2-0",
        'time_zone': pytz.timezone('Europe/Amsterdam'),
        's3_bucket':'iga-fv-stijnvoss',
        's3_region':'us-east-1',
        'evaluation_time_per_individual': .2,  # time need per individual to determine fitness in days
        'population_size': 5,
        'ga_account': '76516435',
        'ga_property': 'UA-76516435-2',
        'ga_profile': '120409781',
        'prefix': '/FV/',
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
            print options
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
