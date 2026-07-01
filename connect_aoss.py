import json
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3


class OpenSearchServerlessClient:
    def __init__(self, host, region, index_name):
        self.host = host
        self.region = region
        self.index_name = index_name
        self.client = self._create_client()

    def _create_client(self):
        service = 'aoss'
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, self.region, service)

        return OpenSearch(
            hosts=[{'host': self.host, 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
        )

    def create_index(self, index_body):
        response = self.client.indices.create(index=self.index_name, body=index_body)
        print('\nCreating index:')
        print(response)
        return response

    def delete_index(self):
        response = self.client.indices.delete(index=self.index_name)
        print('\nDeleting index:')
        print(response)
        return response

    def index_documents(self, file_path='movie.json'):
        with open(file_path, 'r') as f:
            movies = json.load(f)

        for movie in movies:
            response = self.client.index(
                index=self.index_name,
                body=movie,
            )
            print(f'\nIndexed: {movie["title"]}')
            print(response)

    def retrieve_documents(self, query_vector, k=3):
        search_body = {
            "size": k,
            "query": {
                "knn": {
                    "movie-vector": {
                        "vector": query_vector,
                        "k": k
                    }
                }
            }
        }

        response = self.client.search(
            index=self.index_name,
            body=search_body,
        )

        print(f'\nTop {k} similar documents:')
        for hit in response['hits']['hits']:
            print(f"  Score: {hit['_score']}, Title: {hit['_source']['title']}, Year: {hit['_source']['year']}, Location: {hit['_source'].get('location-origin', 'N/A')}")

        return response

    def list_all_documents(self):
        response = self.client.search(
            index=self.index_name,
            body={"size": 10, "query": {"match_all": {}}}
        )
        print(f"\nTotal documents in index: {response['hits']['total']['value']}")
        for hit in response['hits']['hits']:
            print(f"  {hit['_source']}")
        return response

    def test_indexing(self):
        document = {
            'title': 'The Green Mile',
            'director': 'Stephen King',
            'year': 1999,
            'location-origin': {'lat': 34.0522, 'lon': -118.2437},
            'movie-vector': [10, 20, 30]
        }

        response = self.client.index(
            index=self.index_name,
            body=document,
        )
        print('\nTest indexing - The Green Mile:')
        print(response)
        return response


if __name__ == '__main__':
    host = 'rt07p8k488npe50z4e3e.us-east-1.aoss-fips.amazonaws.com'
    region = 'us-east-1'
    index_name = 'movie-embedding-index'

    oss = OpenSearchServerlessClient(host, region, index_name)

    index_body = {
        "settings": {
            "index.knn": True
        },
        "mappings": {
            "properties": {
                "movie-vector": {
                    "type": "knn_vector",
                    "dimension": 3,
                    "space_type": "l2"
                },
                "title": {
                    "type": "text"
                },
                "year": {
                    "type": "long"
                },
                "director": {
                    "type": "text"
                },
                "location-origin": {
                    "type": "geo_point"
                }
            }
        }
    }

    # oss.create_index(index_body)
    # oss.index_documents('movie.json')
    oss.list_all_documents()
    oss.retrieve_documents([3.3, 1.8, 4.2])
    # oss.delete_index()
