from model import  project_setting
from iga import get_IGA
from BF import get_bf
import sys


def run(project):
    sa = project_setting(project, 'search_algorithm')
    if sa == 'IGA':
        iga = get_IGA(project)
        iga.run()
    elif sa == 'BF':
        bf = get_bf(project)
        bf.run()
    else:
        raise Exception("No valid search algorithm found %s" % sa)


# tests
if __name__ == "__main__":
    if len(sys.argv) < 1:
        raise Exception("Expecting project argument")
    else:
         run(sys.argv[1])
