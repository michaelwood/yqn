
# Recommened Install method

$ virtualenv -p /usr/bin/python3 venv
$ source ./venv/bin/activate
$ pip install django==2.1

# To Run:

$ source ./venv/bin/activate
$ cd ./yqnet/
$ ./manage.py migrate
$ ./manage.py runserver

# To load test data
$ ./manage.py loaddata ./test-data.json
