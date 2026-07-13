from generate_embeddings import generate_embedding
from connect_aoss import OpenSearchServerlessClient
import boto3
import json


class SoccerRag:
    def __init__(self, host, region, index_name):
        self.host = host
        self.region = region
        self.index_name = index_name
        self.aoss = OpenSearchServerlessClient(self.host, self.region,
        self.index_name)
        self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
        self.llm_model_id = 'us.amazon.nova-lite-v1:0'

    def getKBContext(self, query_vector, query_field, k):
        return self.aoss.retrieve_documents(query_vector, query_field, k)

    def creatPromptWithoutRAG(self, user_question):
        prompt = f"""You are a helpful soccer expert assistant. Answer the following question about soccer based on your general knowledge. Question: {user_question}"""
        return prompt

    def creatPromptWithRAG(self, user_question, context_snippets):
        context = "\n\n---\n\n".join(context_snippets)

        prompt = f"""You are a helpful soccer expert assistant. Answer the question strictly based on the provided context below. If the answer is not found in the context, say "I don't have enough information to answer that question." Context:
        {context} Question: {user_question}"""
        return prompt

    def invoke_model(self, user_question, context_snippets):
        prompt = self.creatPromptWithRAG(user_question, context_snippets) if context_snippets else self.creatPromptWithoutRAG(user_question)
        request_body = {
            'messages': [
                {
                    'role': 'user',
                    'content': [{'text': prompt}]
                }
            ],
            'inferenceConfig': {
                'maxTokens': 512,
                'temperature': 0.7
            }
        }

        response = self.bedrock.invoke_model(
            modelId=self.llm_model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        content_list = response_body['output']['message']['content']
        text_block = next((item for item in content_list if 'text' in item), None)
        return text_block['text'] if text_block else ''

if __name__ == '__main__':
    soccerRagSystem = SoccerRag('rt07p8k488npe50z4e3e.us-east-1.aoss-fips.amazonaws.com', 'us-east-1', 'soccer-faq-embeddings-index')

    # ask user to submit a query
    user_question = input("\nAsk any question on soccer: ")
    #Who did the most goals in July 1 match Soccer world cup 2026?

    # apply embedding
    query_vector = generate_embedding(user_question)

    # get closest 3 emebddings for the query
    vector_response = soccerRagSystem.getKBContext(query_vector, "embedding", 3)

    # Extract content snippets from the top-k search results
    context_snippets = []
    print(f'\nTop 3 similar documents:')
    for hit in vector_response['hits']['hits']:
        print(f"  filename: {hit['_source']['filename']}")
        context_snippets.append(hit['_source']['content'])

    #Get LLM response without RAG
    response_1 = soccerRagSystem.invoke_model(user_question, [])
    print(f'response with plain LLM: {response_1}')

    #Get LLM response with RAG knowledge
    response_2 = soccerRagSystem.invoke_model(user_question, context_snippets)
    print(f'response with RAG: {response_2}')


        


