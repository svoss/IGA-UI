import sys

import array

from model import models, project_setting, search_space
from fitness import get_fitness
from files import load_pickle, save_pickle
import numpy as np
from deap import creator, base, tools, algorithms
import random

instances = {}


def get_IGA(project):
    if project not in instances:
        if project not in models:
            raise Exception("No project %s exists" % project)
        else:
            instances[project] = IGA(project)
    return instances[project]


def bitstring_to_string(bitstring):
    return [int(b) for b in bitstring.split('-')]


def initIndividual(icls, content):
    return icls(content)


def initPopulation(pcls, ind_init, initial_population):
    return pcls(ind_init(c) for c in initial_population)


class IGA(object):
    """ Responsible for managing the Genetic algorithm"""

    def __init__(self, project):
        """
        :param string project:
        """
        self.project = project
        self.fitness = get_fitness(project)
        self.current_population = False
        # Cross over probability
        self.cxpb = 0.5
        # Mutation probability
        self.mutpb = 0.25
        # Bit flip probability
        self.bitflippb = 0.05

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
        population = [bitstring_to_string(individual) for individual in population_str]
        n = len(population[0])
        fitness = fitness_object.get_fitness(population)
        population = self._ga_selection(population, fitness, n=n, k=k)
        population = ['-'.join([str(i) for i in list(individual)]) for individual in population]
        self._new_population(population)

    def _ga_selection(self, population, fitness, n=4, k=3):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

        toolbox = base.Toolbox()

        toolbox.register("attr_bool", random.randint, 0, 1)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", lambda individual: fitness[population.index(individual)])
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=self.bitflippb)
        toolbox.register("select", tools.selTournament, tournsize=k)

        toolbox.register("population_guess", initPopulation, list, creator.Individual, population)
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

        if self.current_population is False:
            self.current_population = load_pickle(self.project, 'current_population.pkl')
        return self.current_population

    def _new_population(self, population):
        self.current_population = population
        self.fitness.wants_fitness(population)
        save_pickle(self.project, 'current_population.pkl', self.current_population)


# tests
if __name__ == "__main__":
    if len(sys.argv) < 1:
        raise Exception("Expecting project argument")
    else:

        iga = get_IGA(sys.argv[1])
        iga.run()
