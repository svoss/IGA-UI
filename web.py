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
       '    <title>Test it</title>'\
       '</head>'\
       '<body>'\
       '<p> You can make the banner and table disappear by change the 1\s in the code in the query parameters to 0\'s'\
       '    <div id="banner"><b>Banner</b> 1234</div>'\
       '    <table id="table">'\
       '        <tr><td><strong>Table</strong>-</td><td>Bar</td></tr>'\
       '    </table>'\
       'It will influence the javascript file included here'\
       '    <script type="text/javascript" src="/example/'+code+'.js"></script>'\
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
application.add_url_rule('/', 'index', index)
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
