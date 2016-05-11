from model import models
import sys

instances = {}
def get_bf(project):
    if project not in instances:
        if project not in models:
            raise Exception("No project %s exists" % project)
        else:
            instances[project] = BF(project)
    return instances[project]


class BF(object):
    """
    Walks over complete search space
    """


    def __init__(self, project):
        """
        :param string project:
        """
        self.project = project

    def run(self):
        pass