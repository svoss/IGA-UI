from flask import Flask
from flask import Response
from model import models,assemble_js_for_code
from flask import request
app = Flask(__name__)

# print a nice greeting.
def index():
    return 'This is a service used for a project at the Radboud University. You can contact us via ' \
           '<a href="mailto:stijn.voss@student.ru.nl">stijn.voss@student.ru.nl</a>. Or click here for a <a href="example.html">demo</a>'


def example():
    code = request.args.get('code', '1-1')

    return '<html>'\
       '<head>'\
       '    <title>This is test for iga.stijnvoss.com</title>'\
       '</head>'\
       '<body>'\
       '<p>This is demo service used for a project at the Radboud University. You can contact us via ' \
           '<a href="mailto:stijn.voss@student.ru.nl">stijn.voss@student.ru.nl</a></p>'\
       '<p> You can make the banner and table disappear by change the 1\s in the code in the query parameters to 0\'s'\
       '    <div id="banner"><b>Banner</b> 1234</div>'\
       '    <table id="table">'\
       '        <tr><td><strong>Table</strong>-</td><td>Bar</td></tr>'\
       '    </table>'\
       '<p id="colored-text">I want this to be a color</p>'\
       'It will influence the javascript file included here'\
       '    <script type="text/javascript" src="/example/'+code+'.js"></script>'\
       '<script>'\
       '  (function(i,s,o,g,r,a,m){i[\'GoogleAnalyticsObject\']=r;i[r]=i[r]||function(){'\
       '  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),'\
       '  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)'\
       '  })(window,document,\'script\',\'https://www.google-analytics.com/analytics.js\',\'ga\');'\
       ''\
       '  ga(\'create\', \'UA-76516435-2\', \'auto\');'\
       '  ga(\'send\', \'pageview\');'\
       '</script>'\
       '</body>'\
    '</html>'

def individual(project, individual):
    return Response(
        assemble_js_for_code(project,individual),
        status=200,
        mimetype="application/javascript"
    )

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', example)
application.add_url_rule('/example.html', 'example', example)
# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule('/<project>/<individual>.js', 'hello', individual)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
