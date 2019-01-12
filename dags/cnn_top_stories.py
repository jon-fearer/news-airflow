import os
import json
from datetime import datetime, timedelta

import feedparser
from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'Jon Fearer',
    'depends_on_past': False,
    'start_date': datetime(2018, 12, 27),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('cnn_top_stories',
          default_args=default_args,
          schedule_interval=timedelta(days=1))


def get_articles(ds, **kwargs):
    url = 'http://rss.cnn.com/rss/cnn_topstories.rss'
    data = feedparser.parse(url)
    out_path = os.path.join(os.environ['VIRTUAL_ENV'],
                            'data/cnn_top_stories.json')
    with open(out_path, 'w') as fout:
        json.dump(data, fout)


def load_articles(ds, **kwargs):
    in_path = os.path.join(os.environ['VIRTUAL_ENV'],
                           'data/cnn_top_stories.json')
    with open(in_path) as fin:
        data = json.load(fin)
    os.remove(in_path)
    articles = []
    for entry in data['entries']:
        try:
            articles.append([entry['title'],
                             entry['id'],
                             [img for img in entry['media_content']
                              if img['height'] == '250'
                              and img['width'] == '250'][0]['url'],
                             datetime.strptime(
                                entry['published'],
                                '%a, %d %b %Y %H:%M:%S %Z')])
        except (KeyError, IndexError):
            pass
    pg_hook = PostgresHook(postgres_conn_id='news_app',
                           schema='news_app')
    sql = '''insert into news_app_article_staging (title, content_link,
                 thumbnail_link, published_on, created_on, updated_on,
                 publishing_organization_id)
             values (%s, %s, %s, %s, now(), now(), 1);'''
    for article in articles:
        pg_hook.run(sql, parameters=article)


t1 = PythonOperator(
    task_id='get_articles',
    provide_context=True,
    python_callable=get_articles,
    dag=dag)

t2 = PythonOperator(
    task_id='load_articles',
    provide_context=True,
    python_callable=load_articles,
    dag=dag)

t1 >> t2
