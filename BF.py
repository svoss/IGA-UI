from model import models,search_space
import sys
from fitness import get_fitness
from files import load_pickle
import os
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
        self.fitness = get_fitness(project)
        self.search_space = None

    def run(self):

        if self._has_a_search_space():
            self._make_initial_population()
        else:
            self._retrieve_fitness()

        self._plan_next_pop()


    def _has_a_search_space(self):
        return self._get_current_search_space() is None


    def _get_current_search_space(self):
        if self.search_space is None:
            self.search_space = load_pickle(self.project, 'search_space.pkl', None, True)
        return self.search_space


    def _make_initial_population(self):
        pop = search_space(self.project)
        for


    def _get_current_population(self):
        if self.current_population is False:
            self.current_population = load_pickle(self.project, 'current_population.pkl')
        return self.current_population


    def _new_population(self, population):
        self.current_population = population
        self.fitness.wants_fitness(population)
        save_pickle(self.project, 'current_population.pkl', self.current_population)