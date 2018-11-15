import os, sys
#import xml.etree.ElementTree as ET
import qualysapi
import logging
from lxml import etree, objectify

class QualysAPIInventory(object):

  def __init__(self):
    # Configure logging module
    logging.basicConfig(
      filename='qualys_api_inventory.log',
      level=logging.DEBUG,
      format="%(asctime)s:%(levelname)s:%(message)s",
      filemode='a'
    )

  def getAssetHosts(self):
    # Qualys API connection
    qgc = qualysapi.connect('config/qualys_api_config.txt')

    # API url endpoint
    call = '/api/2.0/fo/asset/host/'

    # Parameters
    parameters = {'action': 'list', 'details': 'All'}

    # Get response
    xml_output = qgc.request(call, parameters)

    # Parse response
    self.parseAssetHostsResponse(xml_output)

  def parseAssetHostsResponse(self, xml_output):

    if xml_output is None:
      print('API Reqest Response empty {}'.format(app_get_response))
      logging.error('API Reqest Response empty {}'.format(app_get_response))
      return False

    # Convert XML string Element to ElementTree
    #xml_etree = ET.ElementTree(ET.fromstring(xml_output.content))
    # Get XML root element
    #root = xml_etree.getroot()
    #xml_etree = etree.tostring(xml_output, encoding='unicode')

    # works
    xml_content = xml_output.decode('utf-8').encode('ascii')
    xml_etree = etree.fromstring(xml_content)
    elems = xml_etree.findall('.//HOST')
    print(elems)

    return False

    # Check if response xml is in simple return format if so there is an error message
    if root.tag == 'SIMPLE_RETURN':
      res_code = root.find('./RESPONSE/CODE')
      res_text = root.find('./RESPONSE/TEXT')
      print('API Reqest Response has an error Code: {} Message: {}'.format(res_code.text, res_text.text))
      logging.error('API Reqest Response has an error Code: {} Message: {}'.format(res_code.text, res_text.text))
      return False

    # Traverse XML response structure
    res_host_list = root.find('./RESPONSE/HOST_LIST')
    res_date_time = root.find('./RESPONSE/DATETIME')
    res_next_page_url = root.find('./RESPONSE/WARNING/URL')

    # Initialize empty list to store hosts
    host_list = []

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

def main():

  qualysAPIInventory = QualysAPIInventory()
  qualysAPIInventory.getAssetHosts()

if __name__ == "__main__":
  main()