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
            timeout=60,
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

    def index_documents(self, text_field, file_path='movie.json'):
        import time

        with open(file_path, 'r') as f:
            documents = json.load(f)

        indexed_count = 0
        skipped_count = 0

        for doc in documents:
            # Check if document already exists by text_field (keyword match)
            try:
                search_response = self.client.search(
                    index=self.index_name,
                    body={
                        "query": {
                            "term": {
                                text_field: doc[text_field]
                            }
                        }
                    }
                )

                if search_response['hits']['total']['value'] > 0:
                    print(f'\nSkipped (already exists): {doc[text_field]}')
                    skipped_count += 1
                    continue
            except Exception as e:
                # If search fails (e.g. index just created), proceed with indexing
                print(f'\nSearch check failed, proceeding to index: {e}')

            response = self.client.index(
                index=self.index_name,
                body=doc,
            )
            print(f'\nIndexed: {doc[text_field]}')
            print(response)
            indexed_count += 1

            # Brief pause to allow AOSS eventual consistency
            time.sleep(1)

        print(f'\nSummary: {indexed_count} indexed, {skipped_count} skipped')

    def retrieve_documents(self, query_vector, vector_field, k=3):
        search_body = {
            "size": k,
            "query": {
                "knn": {
                    vector_field: {
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
    host = 'host-placeholder'
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
    # oss.index_documents('title','movie.json')
    oss.list_all_documents()
    response = oss.retrieve_documents([3.3, 1.8, 4.2], 'movie-vector')

    print(f'\nTop 3 similar documents:')
    for hit in response['hits']['hits']:
        print(f"  Score: {hit['_score']}, Title: {hit['_source']['title']}, Year: {hit['_source']['year']}, Location: {hit['_source'].get('location-origin', 'N/A')}")

    # oss.delete_index()
