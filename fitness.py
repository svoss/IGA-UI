from time import time
from model import models, project_setting
from files import load_pickle,save_pickle,log_ga
from ga_api import start_experiments,get_experiment_score
from db import get_db
instances = {}
from pprint import PrettyPrinter


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
        self.db = get_db(project)


    def wants_fitness(self, population=[]):
        """ When you want to gather the fitnesses of the population
            This will set-up an new experiment etc.

            :param population:
        """
        if not self.has_fitness():
            raise Exception('Still running an experiment, can\'t setup a new one')

        hits = self.db.try_to_find_fitness_for(population)

        # Calculate part of population that is not yet cached and should therefore be put in ga
        variations = [p for p in population if p not in hits]

        self._new_experiment(variations)

    def get_fitness(self, population=[]):
        """
        Call this function when you want to retrieve the results of a population
        :param population:
        :return:
        """
        if False:
            raise Exception("Fatal get_fitness called while population not valid")
        else:
            default_population = project_setting(self.project, 'start_code')
            print population
            hits = self.db.try_to_find_fitness_for(population)
            print hits
            # Calculate part of population that is not yet cached and should therefore come from ga
            variations = [p for p in population if p not in hits.keys()]

            # when we need data from google analytics
            if len(variations) > 0:
                log = {}
                ex = self.get_current_experiment()

                # retrieve fitness we need from analytics
                score = get_experiment_score(self.project, ex['experiment_id'])
                experiment_vars = ex['variations']
                base = 0.0
                for i in range(score.shape[1]):
                    if experiment_vars[i] == default_population:
                        base = score[1,i]
                for i in range(score.shape[1]):
                    v = experiment_vars[i]
                    if v in variations:
                        variations.remove(v)

                        hits[v] = self._calc_fitness(score[1,i], base)
                        log[v] = (hits[v], score[1,i], int(score[0,i]))

                # log all results
                self.save_ga(ex['id'], log,base)

            # make sure to return in correct order
            return [hits[p] for p in population]
        return False

    def save_ga(self,ex_id, log, base):
        self.db.ga_experiment_pop_updated(ex_id,log)
        self.db.ga_experiment_finished(ex_id,base,sum([p[2]for p in log.values()]))

    def has_fitness(self):
        ex = self.get_current_experiment()
        return ex is None or ex['ready_on'] < time()


    def get_current_experiment(self):
        ex = self.db.get_ga_open()
        if ex is None:
            return None
        pop = self.db.get_ga_population(ex[0])
        return {
            'id':ex[0],
            'experiment_id': ex[2],
            'variations': pop,
            'ready_on': ex[3]

        }

    def _new_experiment(self, variations=[]):
        # everything is cached, we don't want to send something to analytics now..
        if variations is []:
            pass
        else:
            # default variation is always present and the first
            default_population = project_setting(self.project, 'start_code')

            if default_population in variations:
                variations.remove(default_population)
            variations.insert(0, default_population)

            # start experiment in GA
            ex_id = start_experiments(self.project, variations)
            self._save_current_experiment({"experiment_id":ex_id, "variations":variations})

    def _save_current_experiment(self, ex):
        pop = ex['variations']
        time_per = project_setting(self.project, 'evaluation_time_per_individual')
        id = self.db.save_ga_experiment(ex['experiment_id'], time_per * len(pop) * 86400)
        self.db.save_ga_population(id, pop)


    def _calc_fitness(self, exitRate, baseline):
        return (exitRate - baseline)/baseline



# tests
if __name__ == "__main__":
    f = get_fitness('FV')
