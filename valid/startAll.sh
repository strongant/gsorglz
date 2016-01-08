#start tornado phantomjs_fetcher
#phantomjs lib/phantomjs_fetcher.js 5678 &

#start celery flower
# pip install flower
celery flower -A app.celery --address=127.0.0.1 --port=5555

#start celery worker
celery worker -A app.celery  -l info -Q celery -c 100

#start errand_boy
python -m errand_boy.run

#start Elasticsearch
#https://pypi.python.org/pypi/errand-boy#downloads
#sudo pip install errand_boy
#elasticsearch  -d
#sudo apt-get  install python-psycopg2
#celery worker -A app.celery -Q celery  -l info --logfile logs/celery/celery.log
#celery multi (background)
#(解决mongodb存储任务导致的异常)pip install mongoengine
