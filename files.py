import os
import pickle
from model import project_setting
import boto3
from botocore.exceptions import ClientError
BASE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/projects/"


def load_pickle(project, file):
    """ Loads a pickle file from a project folder

    :param project:
     :param file:
    """
    file = _data_folder(file)
    f = _get_s3_file(project, file)
    if os.path.exists(f):
        with open(f, 'rb') as io:
            return pickle.load(io)

    return None


def save_pickle(project, file, values):
    """ Saves pickle file

    :param project:
    :param file:
    :param values:
    """
    file = _data_folder(file)
    f = _force_folder_exist(project, file)
    with open(f, 'wb') as io:
        pickle.dump(values, io, pickle.HIGHEST_PROTOCOL)

    _save_s3_file(project, file)


def _data_folder(file):
    return os.path.join("data", file)


def _force_folder_exist(project, file):
    """ Gets project folder and also make sure that the path exists"""
    d = _existing_project_path(project)
    full_path = os.path.join(d, file)
    dir = os.path.dirname(full_path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return full_path


def _existing_project_path(project):
    """ Gets project folder and also make sure that the path exists"""
    d = os.path.join(BASE_PATH, project)
    if not os.path.exists(d):
        os.makedirs(d)
    return d


def _save_s3_file(project, file):
    """
    Saves a
    :param project:
    :param file:
    :return:
    """
    b = _s3_connect(project)
    project_path = _existing_project_path(project)
    fs = os.path.join(project_path, file)
    b.upload_file(fs, file)


def _get_s3_file(project, file):
    b = _s3_connect(project)
    fs = _force_folder_exist(project, file)
    try:
        b.download_file(file, fs)
    except ClientError:
        pass
    return fs


def _s3_connect(project):
    return boto3.resource('s3').Bucket(project_setting(project,'s3_bucket'))


def get_service_key_path(project):
    return os.path.join(_existing_project_path(project), 'ga/key.json')

if __name__ == '__main__':
    x = load_pickle('example','current_population.pkl')
    save_pickle('example','current_population.pkl',x)
