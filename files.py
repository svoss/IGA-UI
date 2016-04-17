import os
import pickle
BASE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/projects/"

def load_pickle(project, file):
    """ Loads a pickle file from a project folder"""
    f = os.path.join(_existing_project_path(project), file)
    if os.path.exists(f):
        with open(f, 'rb') as io:
            return pickle.load(io)

    return None

def save_pickle(project, file, values):
    """ Saves pickle file """
    f = os.path.join(_existing_project_path(project), file)
    with open(f, 'wb') as io:
        pickle.dump(values, io, pickle.HIGHEST_PROTOCOL)
    return None

def _existing_project_path(project):
    """ Gets project folder and also make sure that the path exists"""
    d = os.path.join(BASE_PATH,project)
    d = os.path.join(d,'data')
    if not os.path.exists(d):
        os.makedirs(d)
    return d