import sys

import array

from model import models, project_setting, search_space
from fitness import get_fitness
from files import load_pickle, save_pickle
import numpy as np
from deap import creator, base, tools, algorithms
import random
from db import get_db
from csv import writer
from files import _get_s3_file, _save_s3_file
instances = {}


def get_IGA(project):
    if project not in instances:
        if project not in models:
            raise Exception("No project %s exists" % project)
        else:
            instances[project] = IGA(project)
    return instances[project]


def intstring_to_string(intstring):
    return [int(b) for b in intstring.split('-')]


def initIndividual(icls, content):
    return icls(content)


def initPopulation(pcls, ind_init, initial_population):
    return pcls(ind_init(c) for c in initial_population)


def get_int_ranges(project):
    sizes = []
    for item in models[project]:
        size = len(models[project][item])
        sizes.append(size - 1)
    return sizes


class IGA(object):
    """ Responsible for managing the Genetic algorithm"""

    def __init__(self, project):
        """
        :param string project:
        """
        self.project = project
        self.db = get_db(project)
        self.fitness = get_fitness(project)
        self.current_population = False
        # Cross over probability
        self.cxpb = 0.5
        # Mutation probability
        self.mutpb = 0.25
        # Probability
        self.indpb = 0.10

    def run(self):
        """ Function that should be called once in a while, to optionally do a GA iteration if all fitneses are ready"""
        pop = self._get_current_population()
        if pop is None:
            self._make_initial_population()
        else:
            if self.fitness.has_fitness():
                self._iterate_population()

    def _iterate_population(self, k=3):
        fitness_object = get_fitness(self.project)
        population_str = self._get_current_population()
        population = [intstring_to_string(individual) for individual in population_str]
        fitness = fitness_object.get_fitness(population_str)
        # Sometimes fitness can be false if experiment was not complete
        if fitness is not False:
            ranges = get_int_ranges(self.project)
            population = self._ga_selection(population, fitness, ranges, k=k)
            population = ['-'.join([str(i) for i in list(individual)]) for individual in population]
            self._new_population(population)

    def _ga_selection(self, population, fitness, ranges, k=3):
        toolbox = base.Toolbox()

        unique_sizes = set(ranges)
        for size in unique_sizes:
            toolbox.register("attr_int_%s" % size, random.randint, 0, size)
        structure = []
        for size in ranges:
            attr = getattr(toolbox, "attr_int_%s" % size)
            structure.append(attr)

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("individual", array.array, typecode='b', fitness=creator.FitnessMax)
        toolbox.register("individual", tools.initCycle, creator.individual, structure)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", lambda individual: fitness[population.index(individual)])
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutUniformInt, low=[0 for index in range(len(ranges))], up=ranges,
                         indpb=self.indpb)
        toolbox.register("select", tools.selTournament, tournsize=k)

        toolbox.register("population_guess", initPopulation, list, creator.individual, population)
        population = toolbox.population_guess()

        return algorithms.varAnd(population, toolbox, cxpb=self.cxpb, mutpb=self.mutpb)

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
                ind.append(str(np.random.choice(vars[v], 1)[0]))
            pop.append("-".join(ind))
        self._new_population(pop)

    def _get_current_population(self):
        pop = self.db.get_last_population()
        if pop is []:
            return None
        return pop

    def _new_population(self, population):
        self.current_population = population
        self.fitness.wants_fitness(population)
        self.db.insert_new_population(population)


# tests
if __name__ == "__main__":
    if len(sys.argv) < 1:
        raise Exception("Expecting project argument")
    else:
        iga = get_IGA(sys.argv[1])
        iga.run()
        #print iga.db.insert_new_population(iga._get_current_population())

