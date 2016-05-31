import MySQLdb
from model import project_setting
import sys
from time import time
instances = {}


def get_db(project):
    if project not in instances:
        instances[project] = DB(project)
    return instances[project]


class DB(object):
    def __init__(self, project):
        self.project = project
        self.db = MySQLdb.connect(
            host=project_setting(self.project, 'db_host'),
            user=project_setting(self.project, 'db_user'),
            passwd=project_setting(self.project, 'db_password'),
            db=project_setting(self.project, 'db_db')
        )

    def save_ga_experiment(self,  ex_id, finished_in):
        c = self.db.cursor()
        ready_on = int(time())+finished_in

        c.execute("INSERT INTO ga_experiment(ex_id, ready_on, created_on) VALUES(%s, %s, NOW())",(ex_id,ready_on))
        self.db.commit()
        return c.lastrowid

    def save_ga_population(self, ga_ex_id, pop):
        c = self.db.cursor()
        c.executemany("INSERT INTO fitness(code,ga_experiment_id) VALUE(%s,%s)",
                      [(p, ga_ex_id) for p in pop]
                      )
        self.db.commit()

    def get_ga_open(self):
        c = self.db.cursor()
        c.execute("SELECT * FROM ga_experiment WHERE finished IS NULL")
        return c.fetchone()

    def get_ga_population(self, ga_ex_id):
        c = self.db.cursor()
        c.execute("SELECT code FROM fitness WHERE ga_experiment_id = %s",(ga_ex_id,))
        return [s[0] for s in c.fetchall()]

    def ga_experiment_finished(self,ga_ex_id, base_exit_rate,views):
        c = self.db.cursor()
        c.execute("UPDATE ga_experiment SET finished = NOW(), base_exit_rate = %s, total_views = %s WHERE id=%s ", (base_exit_rate, views, ga_ex_id))
        self.db.commit()

    def ga_experiment_pop_updated(self, ga_ex_id, pop):
        c = self.db.cursor()
        c.executemany(
            "UPDATE fitness SET fitness=%s, exit_rate=%s,views=%s WHERE ga_experiment_id=%s AND code=%s",
            [(p[0],p[1],p[2],ga_ex_id,code) for code, p in pop.iteritems()])
        self.db.commit()

    def insert_new_population(self,pop):
        c = self.db.cursor()
        c.execute("INSERT INTO population(created_on) VALUES (NOW())")
        c.executemany(
            "INSERT INTO population_member(population_id, code) VALUES (%s, %s)",
            [(c.lastrowid, p) for p in pop]
        )
        self.db.commit()

    def get_last_population(self):
        c = self.db.cursor()
        c.execute("SELECT m.code FROM population_member m WHERE m.population_id IN (SELECT max(id) FROM population)")
        return [p[0] for p in c.fetchall()]


    def try_to_find_fitness_for(self,pop):
        c = self.db.cursor()
        c.execute("SELECT f.code, f.fitness FROM fitness f WHERE f.code IN %s AND f.fitness IS NOT NULL",(pop,))
        return {x[0]:x[1] for x in c.fetchall()}

if __name__ == "__main__":
    if len(sys.argv) < 1:
        raise Exception("Expecting project argument")
    else:
        db = get_db(sys.argv[1])
        pop = {'0-0-2-2-2-0-2-0':(0.0,0.18664495114006516,3070),
'1-0-0-1-0-0-1-1':(0.16709760827407885,0.18360564940459706,3611),
'0-0-2-0-1-1-0-1':(0.23012281835811246,0.18683932346723042,3784),
'0-1-2-3-0-0-2-0':(0.19036845507433742,0.18293683347005743,3657),
'0-0-3-2-1-0-2-1':(0.27601809954751133,0.1715810879511947,3934)}


        #db.save_ga_experiment(0,'gw7IWGSvQFegRrU8mU2x3Q')
        #db.save_ga_population(1,pop.keys())
        db.ga_experiment_finished(1,18.20447496677005,18056)
        db.ga_experiment_pop_updated(1, pop)




