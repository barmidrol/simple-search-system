# Simple search system ![PONY POWER](http://media.djangopony.com/img/small/badge.png)

## Introduction
Well, this outstanding project is a vain attempt to do pair programming.
The key features will be described later as soon as Sergey Myts uploads full specifications.
Fell free to contribute and ask questions (no one cares).

God help us.

## Running locally

Make sure you have Python installed. Also install the Heroku Toolbelt.

### Main dependencies

* Apache Cassandra (http://cassandra.apache.org/)
* MongoDB (https://www.mongodb.com/)
* RabbitMQ (https://www.rabbitmq.com/)
* Redis (http://redis.io/)

```
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py collectstatic
$ heroku local web
```

If you are facing an error when installing `psycopg2`:

`$ sudo apt-get build-dep python-psycopg2`

## Deploying
Automatic deploy from `master` branch is enabled. The only thing you need to do is to make sure everything works fine.  Just push and see your changes.
