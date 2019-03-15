# qualys-cli
A simple CLI for the purpose of gathering asset inventory from the Qualys API and parsing returned XML into python dictionaries to be imported into other systems.

## Local Development Environment
### Step 1: Copy config file
Based on config-sample.txt create a file config.txt with the hostname, credentials and max retry value. Based on config-sample.py create a file config.py with the API urls.

The config files are excluded from the repository with gitignore. Do not commit the config files to the repository.

### Step 2: Build docker image
```docker build --no-cache -t qualys-local-dev .```

### Step 3: Run Docker container

Run Docker container, mount in local directory into the container as a volume and start a shell
```docker run --rm -it -v "$(pwd)/qualys-api-inventory":/usr/src qualys-local-dev bash```

Run the python script inside the container
```python qualys-inventory.py```

