from googleapiclient.discovery import build
from model import project_setting
from oauth2client.service_account import ServiceAccountCredentials
from files import get_service_key_path
import httplib2
from datetime import datetime
import numpy as np
from files import _get_s3_file, _save_s3_file
from csv import writer
def list_experiments(project):
    """
    List the experiments.

    :param project: Project to list the experiments for.
    :return: A list consisting of all the experiments.
    """
    service = _get_service(project)
    s = service.management().experiments().list(
        accountId=project_setting(project, 'ga_account'),
        webPropertyId=project_setting(project, 'ga_property'),
        profileId=project_setting(project, 'ga_profile')
    ).execute()

    return s.get('items')


def start_experiments(project, variations):
    """
    Start experiments.

    :param project:     The project for which the experiments should start.
    :param variations:  The variations of the experiments (list of variation names).
    :return: Experiment Id.
    """
    service = _get_service(project)
    start_code = project_setting(project, 'start_code')
    base_url = project_setting(project, 'example_url')
    body = {
        'name': 'IGA - ' + datetime.now(project_setting(project, 'time_zone')).strftime('%Y-%m-%d %H:%M:%S'),
        'variations': [{'name': v, 'url': (base_url if start_code == v else '?iga-code=' + v)} for v in variations],
        'servingFramework': 'API',
        'objectiveMetric': 'ga:pageviews',
        'equalWeighting': True,
        'status': 'RUNNING'
    }

    return service.management().experiments().insert(
        accountId=project_setting(project, 'ga_account'),
        webPropertyId=project_setting(project, 'ga_property'),
        profileId=project_setting(project, 'ga_profile'),
        body=body
    ).execute()['id']


def get_experiment_score(project, experiment_id, metrics='ga:pageviews, ga:exitRate'):
    """
    The scores for an experiment.

    :param project: The project to calculate the experiment score for
    :param experiment_id: Id of the experiment to get scores for
    :param metrics: The metrics to use (comma seperated)
    :return: A matrix where the rows are the given metrics and the the columns are the different variants in
             the experiment.
    """
    data = _get_experiment_data(project, experiment_id, metrics=metrics, start_date='2016-01-01',
                                end_date='today')
    metric_names = [metric.strip() for metric in metrics.split(',')]
    matrix = [data['data'][metric_name] for metric_name in metric_names]
    return np.matrix(matrix)


def get_experiment(project, experiment_id):
    """
    Get an experiment.

    :param project: The project
    :param experiment_id: The id of the experiment
    :return: Experiment object
    """
    service = _get_service(project)
    s = service.management().experiments().get(
        accountId=project_setting(project, 'ga_account'),
        webPropertyId=project_setting(project, 'ga_property'),
        profileId=project_setting(project, 'ga_profile'),
        experimentId=experiment_id
    ).execute()

    return s


def stop_experiment(project, experiment_id):
    """
    Get an experiment.

    :param project: The project
    :param experiment_id: The id of the experiment
    :return: (start, end_date)
    """
    service = _get_service(project)
    #get current state, change name to current name appended with end date
    current = get_experiment(project, experiment_id)
    if current['status'] != 'ENDED':
        #get start time from name
        start = datetime.strptime(current['name'], 'IGA - %Y-%m-%d %H:%M:%S')
        end_str = datetime.now(project_setting(project, 'time_zone')).strftime('%Y-%m-%d %H:%M:%S')
        # remove timezone and nanoseconds as we also did in the start
        end = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
        current['name'] = current['name'] + " - " + end_str
        current['status'] = 'ENDED'

        s = service.management().experiments().update(
            accountId=project_setting(project, 'ga_account'),
            webPropertyId=project_setting(project, 'ga_property'),
            profileId=project_setting(project, 'ga_profile'),
            experimentId=experiment_id,
            body=current
        ).execute()
    else:
        dates = current['name'].split(" - ")
        start = datetime.strptime(dates[1], '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(dates[2], '%Y-%m-%d %H:%M:%S')
    vars = [c['name'] for c in current['variations']]
    return vars, start, end


def _log_experiment_results(project, ex_id, start, stop, all_pageviews, all_exitRate ,vars, data):
    f = _get_s3_file(project, 'ga-log.csv')
    # append and optionally create new of if not exists
    with open(f, 'a+') as io:
        w = writer(io)
        for vi in range(len(vars)):
            v = data['index'][vi]
            pv = data['ga:pageviews'][vi]
            per = data['ga:exitRate'][vi]
            w.writerow([ex_id, start, stop, all_pageviews, all_exitRate, v, vars[v], pv, per])
    _save_s3_file(project, 'ga-log.csv')


def _get_experiment_data(project, experiment_id, metrics='ga:pageviews, ga:exitRate', start_date='30daysAgo',
                         end_date='today'):
    """
    Get data for an experiment.

    :param project:         The project to get the data for.
    :param experiment_id:   The ID of the experiment.
    :param metrics:         The metrics which should be retrieved.
    :param start_date:      The start date for which to include data for.
    :param end_date:        The end date for which to include data for.
    :return:
    """
    ids = 'ga:%s' % project_setting(project, 'ga_profile')
    filters = 'ga:experimentId==%s' % experiment_id

    service = _get_service(project)
    s = service.data().ga().get(
        ids=ids,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        dimensions='ga:experimentVariant',
        filters=filters
    ).execute()

    # Modify the rows such that it is possible to do computations on the numbers
    data = {}
    column_names = ['index'] + [metric.strip() for metric in metrics.split(',')]
    for column in column_names:
        data[column] = []
    if 'rows' in s:
        for row in s['rows']:
            for index in range(len(row)):
                value = row[index]
                value = int(value) if index == 0 else float(value)
                column = column_names[index]
                data[column].append(value)
    s['data'] = data
    # Ugly: bounceRate is percentage (not ratio), so convert it to ratios
    if 'ga:bounceRate' in s['data']:
        s['data']['ga:bounceRate'] = [item / 100. for item in s['data']['ga:bounceRate']]

    # Make sessions ints
    if 'ga:sessions' in s['data']:
        s['data']['ga:sessions'] = [int(item) for item in s['data']['ga:sessions']]

    # Ugly: exitRate is percentage (not ratio), so convert it to ratios
    if 'ga:exitRate' in s['data']:
        s['data']['ga:exitRate'] = [item / 100. for item in s['data']['ga:exitRate']]

    # Make sessions ints
    if 'ga:pageviews' in s['data']:
        s['data']['ga:pageviews'] = [int(item) for item in s['data']['ga:pageviews']]

    # stop & log
    vars, start, stop = stop_experiment(project, experiment_id)
    totals = s['totalsForAllResults']
    #_log_experiment_results(project, experiment_id, start.isoformat(), stop.isoformat(), totals['ga:pageviews'], totals['ga:exitRate'], vars, s['data'])
    return s


def remove_experiment(project, experiment_id):
    """
    Remove an experiment.

    :param project: The project
    :param experiment_id: The id of the experiment
    :return: Resource object
    """
    service = _get_service(project)
    s = service.management().experiments().delete(
        accountId=project_setting(project, 'ga_account'),
        webPropertyId=project_setting(project, 'ga_property'),
        profileId=project_setting(project, 'ga_profile'),
        experimentId=experiment_id
    ).execute()

    return s


def _build_service(api_name, api_version, scope, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
      api_name: The name of the api to connect to.
      api_version: The api version to connect to.
      scope: A list auth scopes to authorize for the application.
      key_file_location: The path to a valid service account p12 key file.

    Returns:
      A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scope)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    service = build(api_name, api_version, http=http)

    return service


def _get_service(project):
    """
    Get the service object for a project.

    :param project: Project to get the service object for.
    :return: The service object.
    """
    scope = ['https://www.googleapis.com/auth/analytics.readonly',
             'https://www.googleapis.com/auth/analytics',
             '']
    key_file_location = get_service_key_path(project)

    # Authenticate and construct service.
    return _build_service('analytics', 'v3', scope, key_file_location)


if __name__ == '__main__':
    pass
    #_save_s3_file('FV','ga-log.csv')
    #_save_s3_file('FV', 'pop-log.csv')
    #_get_s3_file('FV')
    print "\n".join([str(x['name']) +":"+ str(x['id']) for x in list_experiments('FV')])
    #x = _get_experiment_data('FV','r9vplR-kQ8aZ1TsK8ZmbbQ' )
