# Dailienator #

The Dailienator is a web-based application used by Sodexo accounts to provide a more easy to use and edit format of they daily event schedule. The format of the output file is as an Excel (xlsx) sheet. 

### Running the Application ###

The application is configured to run locally for development and on Openshift for production.

#### Running Locally ####
*These steps assume that MySQL is installed locally. It should also have a database "dailienator" with access allowed by "root" user.*

1. Create a local folder for logging under the root of the project called "logging". This directory is part of the .gitignore file, so will not be pushed.
1. Create the necessary environment variables for the application including: 
    * DAILIENATOR_SECRET_KEY
    * DAILIENATOR_DEBUG (set to True)
    * DAILIENATOR_ENV (set to 'dev')
    * DAILIENATOR_EMAIL_PASS
1. Create a 32 byte AES key in dailienator/config/catertrax.key.
1. Run ```pip install -r requirements.txt```
1. Create a directory at the root of the project called logging.
1. Run ```./manage.py syncdb```
1. Run ```./manage.py migrate```
1. Run ```./manage.py runserver```

#### Running on Openshift ####

1. Create an Openshift application running Python 2.7.
1. Set the environment variables using ```rhc env set <VARIABLE=VALUE>```
    * DAILIENATOR_SECRET_KEY
    * DAILIENATOR_EMAIL_PASS
    * OPENSHIFT_PYTHON_WSGI_APPLICATION (this must be set to dailienator/wsgi.py) 
1. SSH into the application and create a 32 byte AES key in ${OPENSHIFT_DATA_DIR}catertrax.key
1. Push the project to the Openshift repo.