import os, sys
sys.path.append('./config')
from config import *
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging

class QualysAPIInventory(object):

  def __init__(self):
    # Configure logging module
    logging.basicConfig(
      filename='qualys_api_inventory.log',
      level=logging.DEBUG,
      format="%(asctime)s:%(levelname)s:%(message)s",
      filemode='a'
    )

  def getHosts(self, url_get_hosts):

    auth=(qualys_user, qualys_pwd)
    headers={'X-Requested-With':'Python'}

    app_get_response = self.getHTTP(url=url_get_hosts, params='', headers=headers, auth=auth)
    print app_get_response.content
    print(app_get_response)


  """ Configure requests module to retry session connection """
  def requestsRetrySession(
      self,
      retries=3,
      backoff_factor=0.3,
      status_forcelist=(500, 502, 504),
      session=None,
  ):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

  def getHTTP(self, url='', params='', headers='', auth=''):

    try:
      response = self.requestsRetrySession().get(
          url=url,
          params=params,
          headers=headers,
          auth=auth
      )

    except requests.exceptions.RequestException as e:
      print('getHTTP unable to establish connection to url {}'.format(url))
      logging.error('getHTTP unable to establish connection to url {}'.format(url))
      logging.error('requests.exceptions.RequestException Error: {}'.format(e))
    except Exception as x:
      print('getHTTP unable to establish connection to url {}'.format(url))
      logging.error('getHTTP unable to establish connection to url {}'.format(url))
      logging.error('Error: {} {}'.format(x.__class__.__name__, x))
    else:
        return response
      # Try if response body contains data
      #try:
      #  return response.json()
      # Handle error if deserialization fails (because of no text)
      #except ValueError as valerr:
      #  logging.error(valerr)
        # No results returned
      #  return None


def main():
  # Get Transfer Requests search property and filter value
  url_get_hosts = qualys_url_get_hosts

  qualysAPIInventory = QualysAPIInventory()
  qualysAPIInventory.getHosts(url_get_hosts)

if __name__ == "__main__":
  main()