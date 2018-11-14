import os, sys
sys.path.append('./config')
from config import *
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
import xml.etree.ElementTree as ET

class QualysAPIInventory(object):

  def __init__(self):
    # Configure logging module
    logging.basicConfig(
      filename='qualys_api_inventory.log',
      level=logging.DEBUG,
      format="%(asctime)s:%(levelname)s:%(message)s",
      filemode='a'
    )

  def getHosts(self, qualys_base_url):

    auth=(qualys_user, qualys_pwd)
    headers={'X-Requested-With':'Python'}

    get_hosts_url = qualys_base_url + 'host/?action=list&details=All'

    app_get_response = self.getHTTP(url=get_hosts_url, params='', headers=headers, auth=auth)

    if app_get_response is None:
      print('API Reqest Response empty {}'.format(app_get_response))
      logging.error('API Reqest Response empty {}'.format(app_get_response))
      return False

    # Convert XML string Element to ElementTree
    response_xml = ET.ElementTree(ET.fromstring(app_get_response.content))
    # Get XML root element
    root = response_xml.getroot()

    # Check if response xml is in simple return format if so there is an error message
    if root.tag == 'SIMPLE_RETURN':
      res_code = root.find('./RESPONSE/CODE')
      res_text = root.find('./RESPONSE/TEXT')
      print('API Reqest Response has an error Code: {} Message: {}'.format(res_code.text, res_text.text))
      logging.error('API Reqest Response has an error Code: {} Message: {}'.format(res_code.text, res_text.text))
      return False

    # Traverse XML response structure
    #res_host_list = root[0][1]
    #res_date_time = root[0][0]
    res_host_list = root.find('./RESPONSE/HOST_LIST')
    res_date_time = root.find('./RESPONSE/DATETIME')
    res_next_page_url = root.find('./RESPONSE/WARNING/URL')

    #print(next_page_url.text)

    # Initialize empty list to store hosts
    host_list = []

    count = 0
    # Iterate each host in HOST_LIST of response XML data
    for hosts in res_host_list:
      # Initialize empty dictionary to store a single host row
      host_row = {}
      for host in hosts.iter():
        # Iterate each data value in each host
        if not host.tag == 'HOST':
          # Append each key value pair to to host row dictionary
          # host.tag is the XML element name and host.text is the XML element value
          host_row[host.tag] = host.text
      # Add each host to list of hosts
      host_list.append(host_row)

    print(host_list)


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

  qualysAPIInventory = QualysAPIInventory()
  qualysAPIInventory.getHosts(qualys_base_url)

if __name__ == "__main__":
  main()