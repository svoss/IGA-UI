from time import time
from model import models, project_setting
from files import load_pickle,save_pickle,log_ga
from ga_api import start_experiments,get_experiment_score
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


    def wants_fitness(self, population=[]):
        """ When you want to gather the fitnesses of the population
            This will set-up an new experiment etc.

            :param population:
        """
        if not self.has_fitness():
            raise Exception('Still running an experiment, can\'t setup a new one')

        hits = self._try_get_from_cache(population)

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
            hits = self._try_get_from_cache(population)
            # Calculate part of population that is not yet cached and should therefore come from ga
            variations = [p for p in population ]#if p not in hits.keys()]

            # when we need data from google analytics
            if len(variations) > 0:
                ex = self.get_current_experiment()

                # retrieve fitness we need from analytics
                score = get_experiment_score(self.project, ex['experiment_id'])
                experiment_vars = ex['variations']
                base = 0.0
                for i in range(score.shape[1]):
                    if experiment_vars[i] == default_population:
                        base = score[0,i]
                for i in range(score.shape[1]):
                    v = experiment_vars[i]
                    if v in variations:
                        variations.remove(v)
                        hits[v] = self._calc_fitness(score[0,i], base)
                print variations
                if len(variations) > 0:
                    log_ga(self.project, "Could not find all fitnesses, re-planning for a day")
                    self._set_finished_in(86400)
                else:
                    # log all results
                    log_ga(self.project, score)
                    self._save_cache(hits)

                    #make sure to return in correct order
                    return [hits[p] for p in population]
        return False

    def has_fitness(self):
        if self._get_finished() < time():
            return self._get_finished(True) < time()


    def get_current_experiment(self):
        return load_pickle(self.project, 'current_ga_experiment.pkl')

    def _new_experiment(self, variations=[]):
        # everything is cached, we don't want to send something to analytics now..
        if variations is []:
            self._set_finished_in(0)
        else:
            # default variation is always present and the first
            default_population = project_setting(self.project, 'start_code')

            if default_population in variations:
                variations.remove(default_population)
            variations.insert(0, default_population)

            # start experiment in GA
            ex_id = start_experiments(self.project, variations)
            self._save_current_experiment({"experiment_id":ex_id, "variations":variations})

            # experiment finish time will dependent on the number of variations available
            # 'evaluation_time_per_individual' setting gives the days it takes to evaluate one ind. in a population
            time_per = project_setting(self.project, 'evaluation_time_per_individual')
            self._set_finished_in(time_per * len(variations) * 86400)

    def _save_current_experiment(self, ex):
        save_pickle(self.project, 'current_ga_experiment.pkl',ex)

    def _set_finished_in(self,in_secs=0):
        save_pickle(self.project,'finished.pkl',time()+in_secs)

    def _get_finished(self, forceS3 = False):
        return load_pickle(self.project, 'finished.pkl',0, forceS3)

    def _save_cache(self, fitnesses):
        save_pickle(self.project,'fitness_cache.pkl',fitnesses )


    def _try_get_from_cache(self, population=[]):
        cache = load_pickle(self.project, 'fitness_cache.pkl')
        if cache is not None:
            return dict([(k,v) for k,v in cache.iteritems() if k in population])
        return {}

    def _calc_fitness(self, exitRate, baseline):
        return (exitRate - baseline)/baseline



# tests
if __name__ == "__main__":
    cache = load_pickle('FV', 'fitness_cache.pkl')
    print cache
    f = get_fitness('FV')
    #print f._set_finished_in(0)
    print time()
    print f._get_finished()
