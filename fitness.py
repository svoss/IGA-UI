import sys
from model import models


instances = {}


def get_fitness(project):
    if project not in instances:
        if project not in models:
            raise Exception("No project %s exists" % project)
        else:
            instances[project] = Fitness(project)
    return instances[project]

class Fitness(object):
    """
    Responsible for retrieving the fitness for certain individuals
    """
    def __init__(self, project):
        """
        :param string project:
        """
        self.project = project

    def wants_fitness(self, population = []):
        """ When you want to gather the fitnesses of the population
            This will set-up an new experiment etc.
        """
        pass
    def get_fitness(self, population = []):
        """

        :param population:
        :return:
        """

        return {}

    def has_fitness(self, population = []):
        return False

    def get_current_experiment(self):
        return {
            "experiment_id":"fPnYQqFiQOuv9ziF2Meziw",
            "variations" : ["0-0-0","0-0-1"]
        }

# tests
if __name__ == "__main__":
    f = get_fitness('example')
