import sys
from model import models, project_setting,search_space
from fitness import get_fitness
from files import load_pickle,save_pickle
import numpy as np
instances = {}


def get_IGA(project):
    if project not in instances:
        if project not in models:
            raise Exception("No project %s exists" % project)
        else:
            instances[project] = IGA(project)
    return instances[project]


class IGA(object):
    """ Responsible for managing"""
    def __init__(self, project):
        """
        :param string project:
        """
        self.project = project
        self.fitness = get_fitness(project)
        self.current_population = False

    def run(self):
        """ Function that should be called once in a while, to optionally do a GA iteration if all fitneses are ready"""

        pop = self._get_current_population()
        print pop
        if pop is None:
            self._make_initial_population()
        else:
            if self.fitness.has_fitness(pop):
                self._iterate_population()



    def _iterate_population(self):
        # here we are going to mutate
        pass

    def _make_initial_population(self):
        pop_size = project_setting(self.project, 'population_size')
        start_code = project_setting(self.project, 'start_code')
        vars = search_space(self.project)

        # start code is always in population
        pop = [start_code]

        # rest are randomly generated samples
        for i in xrange(0, pop_size - 1):
            ind = []
            for v in vars:
                ind.append(str(np.random.choice(vars[v],1)[0]))
            pop.append("-".join(ind))
        self._new_population(pop)


    def _get_current_population(self):

        if self.current_population is False:
            self.current_population = load_pickle(self.project, 'current_population.pkl')
        return self.current_population

    def _new_population(self, population):
        self.current_population = population
        self.fitness.wants_fitness(population)
        save_pickle(self.project,'current_population.pkl', self.current_population)

# tests
if __name__ == "__main__":
    if len(sys.argv) < 1:
        raise Exception("Expecting project argument")
    else:

        iga = get_IGA(sys.argv[1])
        iga.run()
