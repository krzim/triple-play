from copy import deepcopy

from elasticsearch import Elasticsearch as ElasticsearchClient
from elasticsearch_dsl import Search

import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")
# Warning: This app is untested and is still in development!
class Elasticsearch(AppBase):
    def __init__(self, app_name=None, device_id=None):
        super(Elasticsearch, self).__init__(app_name, device_id)
        connection = deepcopy(self.device_fields)
        if 'url_prefix' in connection and not connection['url_prefix']:
            connection.pop('url_prefix')
        self.es = ElasticsearchClient([connection])

    def create_search(index=None, doc_type=None):
    return Search(index=index, doc_type=doc_type).to_dict(), 'Success'


    def add_query_to_search(self, search, terms, query_type='match'):
        search = Search.from_dict(search)
        return search.query(query_type, **terms).to_dict(), 'Success'


    def add_filter_to_search(self, search, terms, filter_type='term'):
        search = Search.from_dict(search)
        return search.filter(filter_type, **terms).to_dict(), 'Success'


    def add_exclusion_to_search(self, search, terms, exclude_type='terms'):
        search = Search.from_dict(search)
        return search.exclude(exclude_type, **terms).to_dict(), 'Success'


    def add_bucket_to_search(self, search, aggregation_name, aggregation_type, terms):
        search = Search.from_dict(search)
        return search.aggs.bucket(aggregation_name, aggregation_type, **terms).to_dict(), 'Success'


    def add_metric_to_search(self, search, metric_name, metric_type, terms):
        search = Search.from_dict(search)
        return search.aggs.metric(metric_name, metric_type, **terms).to_dict(), 'Success'


    def add_pipeline_to_search(self, search, pipeline_name, pipeline_type, buckets_path):
        search = Search.from_dict(search)
        return search.aggs.pipeline(pipeline_name, pipeline_type, buckets_path=buckets_path), 'Success'


    def add_sort_to_search(self, search, sort_field, terms, sort_type='category'):
        search = Search.from_dict(search)
        return search.sort(sort_type, sort_field, **terms).to_dict(), 'Success'


    def add_pagination_to_search(self, search, start_result, end_result):
        search = Search.from_dict(search)
        return search[start_result: end_result].to_dict(), 'Success'


    def add_term_suggestion_to_search(self, search, suggestion_name, suggestor_text, term):
        search = Search.from_dict(search)
        return search.suggest(suggestion_name, suggestor_text, term=term).to_dict(), 'Success'


    def add_phrase_suggestion_to_search(self, search, suggestion_name, suggestor_text, phrase):
        search = Search.from_dict(search)
        return search.suggest(suggestion_name, suggestor_text, phrase=phrase).to_dict(), 'Success'


    def add_completion_suggestion_to_search(self, search, suggestion_name, suggestor_text, completion):
        search = Search.from_dict(search)
        return search.suggest(suggestion_name, suggestor_text, completion=completion).to_dict(), 'Success'


    def create(self, index, doc_type, body, entry_id=None):
        if id is not None:
            args = {'index': index, 'doc_type': doc_type, 'body': body, 'id': entry_id}
        else:
            args = {'index': index, 'doc_type': doc_type, 'body': body}
        return self.es.create(**args), 'Success'


    def create_many(self, index, doc_type, data):
        args = {'index': index, 'doc_type': doc_type}
        ret = []
        for body in data:
            args.update(body=body)
            ret.append(self.es.create(**args))
        return ret, 'Success'


    def delete(self, index, doc_type, entry_id):
        return self.es.delete(index=index, doc_type=doc_type, id=entry_id), 'Success'


    def delete_many(self, index, doc_type, entry_ids):
        return [self.es.delete(index=index, doc_type=doc_type, id=entry_id) for entry_id in entry_ids], 'Success'


    def get(self, index, entry_id, doc_type='_all'):
        return self.es.get(index=index, doc_type=doc_type, id=entry_id), 'Success'


    def ping(self):
        return 'Cluster is up', 'Up' if self.es.ping() else 'Cluster is down', 'Down'


    def search(self, search):
        search = Search.from_dict(search)
        search.using(self.es)
        response = search.execute()
        if response.success():
            return response.to_dict(), 'Success'
        else:
            return 'Search error', 'SearchError'


    def delete_by_search(self, search):
        search = Search.from_dict(search)
        search.using(self.es)
        response = search.delete()
        if response.success():
            return response.to_dict(), 'Success'
        else:
            return 'Search error', 'SearchError'
