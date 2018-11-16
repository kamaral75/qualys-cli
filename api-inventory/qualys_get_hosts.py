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
      filemode='w'
    )

  def getAssetHosts(self, id_min, page_number, host_list):

    # Initialize xml output
    xml_output = None

    # Qualys API connection
    qgc = qualysapi.connect('config/qualys_api_config.txt')

    # Check if this iteration is the first page of results
    if id_min == 1:
      print('Getting first page of results id_min {}'.format(id_min))
      logging.info('Getting first page of results id_min {}'.format(id_min))

    # Increment page number
    page_number = page_number + 1

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
      self.parseAssetHostsResponse(page_number, host_list, xml_output)

    # Check if output is empty
    if xml_output is None:
      print('QualysAPI returned an empty response {}'.format(xml_output))
      logging.error('QualysAPI returned an empty response {}'.format(xml_output))
      return False


  def parseAssetHostsResponse(self, page_number, host_list, xml_output):

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

        print('Getting next page of results page_number {} id_min {}'.format(page_number, id_min_next))
        logging.info('Getting next page of results page_number {} id_min {}'.format(id_min_next))

        # Get next page of results
        self.getAssetHosts(id_min_next, page_number, host_list)

      # Else if next page url is empty
      else:
        print('Last page of results page_number {} id_min {}'.format(page_number, id_min_next))
        logging.info('Last page of results page_number {} id_min {}'.format(page_number, id_min_next))
        print('Returning host list')
        logging.info('Returning host list')

        return(host_list)

    # Check if there were any errors getting the url
    except IndexError as indxerr:
      logging.info('Unable to get pagination url id_min. Error: {}'.format(indxerr))

def main():
  # Initialize QualysAPIInventory class
  qualysAPI = QualysAPI()
  # Start with first host id 1 and empty host list
  qualysAPI.getAssetHosts(1, 0, [])

if __name__ == "__main__":
  main()