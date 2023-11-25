import pysolr
from datetime import datetime


class SearchService:
    def __init__(self, config, model_loader):
        self.solr = pysolr.Solr(config['SOLR_URL'], timeout=10)
        self.model_loader = model_loader

    def bm25_search(self, query_text):
        query_params = {
            'q': query_text,
            'defType': 'edismax',
            'qf': 'title^2 content summary',
            'pf': 'title^2 content summary',
            'fl': 'id,title,feed,url,score,created_at',
            # 'fq': 'created_at:[2020-01-01T00:00:00Z TO 2020-12-31T23:59:59Z]',
            'fq': 'created_at:[NOW-3YEAR TO NOW]',
            'rows': 10
        }

        # Execute the query
        results = self.solr.search(**query_params)

        for result in results:
            result['created_at'] = self.convert_date_str(result['created_at'])

        return results

    def vector_search(self, query_text):
        tokens = self.model_loader.tokenize(query_text)

        embeddings = self.model_loader.generate_embeddings(query_text)
        query_params = {
            'q': '{!knn f=par_embeddings_dp topK=1000}' + str(embeddings),
            'fl': "id,title,feed,url,score,created_at",
#            'fq': 'created_at:[2020-01-01T00:00:00Z TO 2020-12-31T23:59:59Z]',
            'fq': 'created_at:[NOW-3YEAR TO NOW]',
            'rows': 10
        }

        results = self.solr.search(**query_params)

        for result in results:
            result['created_at'] = self.convert_date_str(result['created_at'])

        return tokens, results

    def convert_date_str(self, date_str):
        date_object = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = date_object.strftime("%Y-%m-%d")
        return formatted_date
