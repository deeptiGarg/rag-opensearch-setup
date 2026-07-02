import json
import boto3

region = 'us-east-1'
bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
s3 = boto3.client('s3', region_name=region)
MODEL_ID = 'amazon.titan-embed-text-v2:0'

BUCKET_NAME = 'faq-s3-for-rag'

def read_faq_documents_from_s3():
    documents = []
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.endswith('.md'):
            file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            content = file_obj['Body'].read().decode('utf-8')
            documents.append({'filename': key, 'content': content})

    return documents


def generate_embedding(text):
    body = json.dumps({
        'inputText': text,
        'dimensions': 1024,
        'normalize': True
    })

    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        contentType='application/json',
        accept='application/json',
        body=body
    )

    response_body = json.loads(response['body'].read())
    return response_body['embedding']


def main():
    documents = read_faq_documents_from_s3()
    print(f'Loaded {len(documents)} documents\n')

    results = []
    for doc in documents:
        embedding = generate_embedding(doc['content'])
        results.append({
            'filename': doc['filename'],
            'content': doc['content'],
            'embedding': embedding
        })
        print(f"Generated embedding for {doc['filename']} - vector dimension: {len(embedding)}")

    # Save embeddings to file
    with open('faq_embeddings.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f'\nSaved {len(results)} embeddings to faq_embeddings.json')


if __name__ == '__main__':
    main()
