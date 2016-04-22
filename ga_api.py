from model import project_setting
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from files import get_service_key_path
import httplib2
from datetime import datetime


def list_experiments(project):
    service = _get_service(project)
    s = service.management().experiments().list(
        accountId=project_setting(project, 'ga_account'),
        webPropertyId=project_setting(project, 'ga_property'),
        profileId=project_setting(project, 'ga_profile')
    ).execute()

    for i in s.get('items'):
        print i


def start_experiments(project, variations):
    service = _get_service(project)
    body = {
        'name': 'IGA - ' + datetime.now(project_setting(project, 'time_zone')).strftime('%Y-%m-%d %H:%M:%S'),
        'variations': [{'name': v} for v in variations],
        'servingFramework': 'API',
        'objectiveMetric': 'ga:bounces',
        'status': 'RUNNING'
    }

    s = service.management().experiments().insert(
        accountId=project_setting(project, 'ga_account'),
        webPropertyId=project_setting(project, 'ga_property'),
        profileId=project_setting(project, 'ga_profile'),
        body=body
    ).execute()

def get_experiment_score(project):
    pass

def get_experiment(project):
    pass


def remove_experiment(project):
    pass


def _build_service(api_name, api_version, scope, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
      api_name: The name of the api to connect to.
      api_version: The api version to connect to.
      scope: A list auth scopes to authorize for the application.
      key_file_location: The path to a valid service account p12 key file.
      service_account_email: The service account email address.

    Returns:
      A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scope)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    service = build(api_name, api_version, http=http)

    return service


def _get_service(project):
    scope = ['https://www.googleapis.com/auth/analytics.readonly',
             'https://www.googleapis.com/auth/analytics',
             '']
    key_file_location = get_service_key_path(project)

    # Authenticate and construct service.
    return _build_service('analytics', 'v3', scope, key_file_location)


if __name__ == '__main__':
    list_experiments('example')
