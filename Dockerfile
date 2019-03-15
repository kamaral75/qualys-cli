# Base image
FROM python:2.7-alpine

# Install requirements for lxml
RUN apk add --no-cache gcc musl-dev libxslt-dev && pip install pip==10.0.1

# Install Python modules
# QualysAPI
RUN pip2.7 install qualysapi
# Requirement for lxml
RUN pip2.7 install six
# XML parser
RUN pip2.7 install lxml

# Copy code from repository to image
COPY ./qualys-api-inventory /usr/src

# Start in default source directory
WORKDIR /usr/src/
