from connect_aoss import OpenSearchServerlessClient

class DataIngestionIntoOpenSearch:
    def __init__(self):
        self.host = "host-placeholder"
        self.region = "us-east-1"
        self.index_name = "soccer-faq-embeddings-index"
        self.oss = OpenSearchServerlessClient(self.host, self.region, self.index_name)

    def create_vector_index(self):
        index_body = {
            "settings": {
                "index.knn": True
            },
            "mappings": {
                "properties": {
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 1024,
                        "space_type": "l2"
                    },
                    "filename": {
                        "type": "keyword"
                    },
                    "content": {
                        "type": "text"
                    }
                }
            }
        }
        
        self.oss.create_index(index_body)

    def ingest(self):
        # create index
        #self.create_vector_index()
        # add docs for indexing
        self.oss.index_documents(text_field='filename',file_path='faq_embeddings.json')
        # view data in index
        self.oss.list_all_documents()
        
if __name__ == '__main__':
    dataIngestion = DataIngestionIntoOpenSearch()
    dataIngestion.ingest()
