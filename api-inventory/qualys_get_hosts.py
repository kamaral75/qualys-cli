import os, sys
import xml.etree.ElementTree as ET
import qualysapi
import logging

class QualysAPI(object):

  def __init__(self):
    # Configure logging module
    logging.basicConfig(
      filename='qualys_api_inventory.log',
      level=logging.DEBUG,
      format="%(asctime)s:%(levelname)s:%(message)s",
      filemode='a'
    )

  def getAssetHosts(self, id_min, host_list):

    # Qualys API connection
    try:
      qgc = qualysapi.connect('config/qualys_api_config.txt')

    except Exception as x:
      print('Unable to connect to QualysAPI. Check hostname and credentials in configuration file. Error: {}'.format(x))
      logging.error('Unable to connect to QualysAPI. Check hostname and credentials in configuration file. Error: {}'.format(x))

    # Check if this iteration is the first page of results
    if id_min == 1:
      print('Getting first page of results id_min {}'.format(id_min))
      logging.info('Getting first page of results id_min {}'.format(id_min))

    # API url endpoint
    call = '/api/2.0/fo/asset/host/'

    # Parameters
    parameters = {'action': 'list', 'details': 'All', 'id_min': id_min}

    # Get response
    xml_output = qgc.request(call, parameters)

    # Parse response
    self.parseAssetHostsResponse(xml_output, host_list)

  def parseAssetHostsResponse(self, xml_output, host_list):

    if xml_output is None:
      print('API Reqest Response empty {}'.format(app_get_response))
      logging.error('API Reqest Response empty {}'.format(app_get_response))
      return False

    # Convert XML string Element to ElementTree
    xml_etree = ET.ElementTree(ET.fromstring(xml_output))

    # Get XML root element
    root = xml_etree.getroot()

    # Check if response xml is in simple return format if so there is an error message
    if root.tag == 'SIMPLE_RETURN':
      res_code = root.find('./RESPONSE/CODE')
      res_text = root.find('./RESPONSE/TEXT')
      print('API Reqest Response has an error Code: {} Message: {}'.format(res_code.text, res_text.text))
      logging.error('API Reqest Response has an error Code: {} Message: {}'.format(res_code.text, res_text.text))
      return False

    # Traverse XML response structure
    res_host_list = root.findall('.//HOST')
    res_date_time = root.find('./RESPONSE/DATETIME')

    # Initialize empty list to store hosts
    #host_list = []

    # Iterate each host in HOST_LIST of response XML data
    for hosts in res_host_list:
      # Initialize empty dictionary to store a single host row
      host_row = {}
      # Iterate host list
      for host in hosts.iter():
        if not host.tag == 'HOST':
          # Append each key value pair to to host row dictionary
          # host.tag is the XML element name and host.text is the XML element value
          host_row[host.tag] = host.text
      # Add each host to list of hosts
      host_list.append(host_row)

    #print(host_list)

    try:
      # Get next page url from response
      res_next_page_url = root.find('./RESPONSE/WARNING/URL')

      if res_next_page_url is not None:
        url = res_next_page_url.text
        # Parse url to get the new id_min value
        start = url.find('id_min') + 7
        end = url.find('&',start)
        id_min = int(url[start:end])

        print('Getting next page of results id_min {}'.format(id_min))
        logging.info('Getting next page of results id_min {}'.format(id_min))

        # Get next page of results
        self.getAssetHosts(id_min, host_list)

      else:
        print('Last page of results. Returning host list.')
        return(host_list)

    # If there is no last page the url will not have a value
    except IndexError, e:
      print('Unable to get pagination url id_min. Error: {}'.format(e))

def main():
  # Initialize QualysAPIInventory class
  qualysAPI = QualysAPI()
  # Start with first host id 1 and empty host list
  qualysAPI.getAssetHosts(1, [])

if __name__ == "__main__":
  main()