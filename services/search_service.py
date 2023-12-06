import pysolr
from datetime import datetime


class SearchService:
    def __init__(self, config, model_loader):
        self.solr = pysolr.Solr(config['SOLR_URL'], timeout=90)
        self.model_loader = model_loader

    def bm25_search(self, query_text, date_filter):
        query_params = {
            'q': query_text,
            'defType': 'edismax',
            'qf': 'title^2 content summary',
            'pf': 'title^2 content summary',
            'fl': 'id,title,feed,url,score,created_at',
            'rows': 10
        }

        if date_filter:
            query_params['fq'] = f"created_at:[NOW-{date_filter} TO NOW]"

        # Execute the query
        results = self.solr.search(**query_params)

        for result in results:
            result['created_at'] = self.convert_date_str(result['created_at'])

        return results

    def vector_search(self, query_text, date_filter):
        tokens = self.model_loader.tokenize(query_text)

        embeddings = self.model_loader.generate_embeddings(query_text)
        query_params = {
            'q': '{!knn f=par_embeddings_dp topK=500}' + str(embeddings),
            'fl': "id,title,feed,url,score,created_at",
            'rows': 10
        }

        if date_filter:
            query_params['fq'] = f"created_at:[NOW-{date_filter} TO NOW]"

        results = self.solr.search(**query_params)

        for result in results:
            result['created_at'] = self.convert_date_str(result['created_at'])

        return tokens, results

    def hybrid_search_rerank(self, query_text, date_filter):

        embeddings = self.model_loader.generate_embeddings(query_text)
        query_params = {
            'rqq': '{!knn f=par_embeddings_dp topK=10000}' + str(embeddings),
            'rq': '{!rerank reRankQuery=$rqq reRankDocs=500 reRankWeight=30}',
            'q': '{!edismax qf=\'title^2 content summary\' pf=\'title^2 content summary\'}' + f'({query_text})',
            'fl': "id,title,feed,url,score,created_at",
            'rows': 10
        }

        if date_filter:
            query_params['fq'] = f"created_at:[NOW-{date_filter} TO NOW]"

        results = self.solr.search(**query_params)

        for result in results:
            result['created_at'] = self.convert_date_str(result['created_at'])

        return results


    def hybrid_search(self, query_text, date_filter):

        embeddings = self.model_loader.generate_embeddings(query_text)
        query_params = {
            'q1': '{!knn f=par_embeddings_dp topK=10000}' + str(embeddings),
            'q2': '{!edismax qf=\'title^2 content summary\' pf=\'title^2 content summary\' mm=\'40%\'}' + f' v=\'{query_text}\'',
            'q': '_query_:"${q2}" OR (_query_:"${q1}")^50',
            # 'q': '{!bool should=$q1 should=$q2}',
            'fl': "id,title,feed,url,score,created_at",
            'rows': 10
        }

        if date_filter:
            query_params['fq'] = f"created_at:[NOW-{date_filter} TO NOW]"

        results = self.solr.search(**query_params)

        for result in results:
            result['created_at'] = self.convert_date_str(result['created_at'])

        return results

    def convert_date_str(self, date_str):
        date_object = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = date_object.strftime("%Y-%m-%d")
        return formatted_date
