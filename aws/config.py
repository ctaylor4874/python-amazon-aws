import os

# Write responses to the XML_RESPONSE_DIR
WRITE_RESPONSES = True
# Directory where the responses from make_request in AWS are written.
XML_RESPONSE_DIR = os.path.join(os.path.dirname(__file__), 'xml-responses')

if not os.path.exists(XML_RESPONSE_DIR):
    os.mkdir(XML_RESPONSE_DIR)
