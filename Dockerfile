FROM python:2.7-alpine
  
# Install curl
#RUN apk add --no-cache bash curl tzdata

# Install Python modules
RUN pip2.7 install requests

# Fix the timezone
#RUN rm -f /etc/localtime \
#    && ln -s /usr/share/zoneinfo/America/New_York /etc/localtime

# Copy code from repository to image
COPY ./api-inventory /usr/src

# Start in default source directory
WORKDIR /usr/src/
