import os, sys
import xml.etree.ElementTree as ET
import qualysapi
import logging

class QualysAPI(object):

  def __init__(self):
    # Configure logging module
    logging.basicConfig(
      filename='logs/qualys_api_inventory.log',
      level=logging.DEBUG,
      format="%(asctime)s:%(levelname)s:%(message)s",
      filemode='w'
    )

  def getAssetIDs(self):

    # Initialize xml output
    xml_output = None

    # Qualys API connection
    qgc = qualysapi.connect('config/config.txt')

    call = '/qps/rest/2.0/get/am/hostasset/77701130'

    #parameters = '<ServiceRequest><filters><Criteria field="lastVulnScan" operator="LESSER">1999-01-01</Criteria></filters></ServiceRequest>'
    parameters = '{}'

    # Get response
    try:
      xml_output = qgc.request(call, parameters)

    except Exception as x:
      print('Unable to connect to QualysAPI. Check hostname and credentials in configuration file. Error: {}'.format(x))
      logging.error('Unable to connect to QualysAPI. Check hostname and credentials in configuration file. Error: {}'.format(x))
      return False

    # Check if output is empty
    if xml_output is None:
      print('QualysAPI returned an empty response {}'.format(xml_output))
      logging.error('QualysAPI returned an empty response {}'.format(xml_output))
      return False

    print(xml_output)
    return False


  def getAssetHosts(self, id_min, host_list):

    # Initialize xml output
    xml_output = None

    # Qualys API connection
    qgc = qualysapi.connect('config/qualys_api_config.txt')

    # Check if this iteration is the first page of results
    if id_min == 1:
      print('Getting first page of results id_min {}'.format(id_min))
      logging.info('Getting first page of results id_min {}'.format(id_min))

    # API url endpoint
    call = '/api/2.0/fo/asset/host/'

    # Parameters
    parameters = {'action': 'list', 'details': 'All', 'id_min': id_min}

    # Get response
    try:
      xml_output = qgc.request(call, parameters)

    except Exception as x:
      print('Unable to connect to QualysAPI. Check hostname and credentials in configuration file. Error: {}'.format(x))
      logging.error('Unable to connect to QualysAPI. Check hostname and credentials in configuration file. Error: {}'.format(x))
      return False

    # Check if response is not empty
    if xml_output is not None:
      # Parse response
      self.parseAssetHostsResponse(host_list, xml_output)

    # Check if output is empty
    if xml_output is None:
      print('QualysAPI returned an empty response {}'.format(xml_output))
      logging.error('QualysAPI returned an empty response {}'.format(xml_output))
      return False

    print(xml_output)
    return False

  def parseAssetHostsResponse(self, host_list, xml_output):

    # Initialize next page url
    res_next_page_url = None

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

    try:
      # Get next page url from response
      res_next_page_url = root.find('./RESPONSE/WARNING/URL')

      # Check if next page url is not empty
      if res_next_page_url is not None:
        url = res_next_page_url.text
        # Parse url to get the new id_min value
        start = url.find('id_min') + 7
        end = url.find('&',start)
        id_min_next = int(url[start:end])

        print('Getting next page of results id_min {}'.format(id_min_next))
        logging.info('Getting next page of results id_min {}'.format(id_min_next))

        # Get next page of results
        self.getAssetHosts(id_min_next, host_list)

      # Else if next page url is empty
      else:
        print('Last page of results has been reached. Returning host list.')
        logging.info('Last page of results has been reached. Returning host list.')

        print(host_list)

    # Check if there were any errors getting the url
    except IndexError as idxerr:
      logging.info('Unable to get pagination url id_min. Error: {}'.format(idxerr))

def main():
  # Initialize QualysAPIInventory class
  qualysAPI = QualysAPI()
  # Start with first host id 1 and empty host list
  #qualysAPI.getAssetHosts(1, [])
  qualysAPI.getAssetIDs()

if __name__ == "__main__":
  main()