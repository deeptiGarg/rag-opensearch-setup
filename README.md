# rag-opensearch-setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install opensearch-py
```

### match-all query
``
  {'movie-vector': [2.1, 4.5, 6.7], 'title': 'The Shawshank Redemption', 'year': 1994, 'location-origin': {'lat': 40.7128, 'lon': -74.006}}
  {'movie-vector': [4.0, 2.9, 3.1], 'title': 'Interstellar', 'year': 2014, 'location-origin': {'lat': 37.7749, 'lon': -122.4194}}
  {'title': 'The Green Mile', 'director': 'Stephen King', 'year': '1996', 'location-origin': '47.71, 122.00', 'movie-vector': [10, 20, 30]}
  {'movie-vector': [1.2, 3.4, 5.6], 'title': 'Dead Man Walking', 'year': 1999, 'location-origin': {'lat': 34.0522, 'lon': -118.2437}}
  {'movie-vector': [3.3, 1.8, 4.2], 'title': 'Inception', 'year': 2010, 'location-origin': {'lat': 51.5074, 'lon': -0.1278}}

``

### Retreive documents based on given embedding
``
Top 3 similar documents:
  Score: 1.0, Title: Inception, Year: 2010, Location origin: {'lat': 51.5074, 'lon': -0.1278}
  Score: 0.25575447, Title: Interstellar, Year: 2014, Location origin: {'lat': 37.7749, 'lon': -122.4194}
  Score: 0.10070493, Title: Dead Man Walking, Year: 1999, Location origin: {'lat': 34.0522, 'lon': -118.2437}

``