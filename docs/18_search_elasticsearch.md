# 18 — Search with Elasticsearch (Complete In-Depth Guide)

> 🎯 **Goal**: Powerful full-text search add karo apni app mein - Google jaisi search!

---

## 📚 Table of Contents
1. [Search Kyun Important?](#search-kyun-important)
2. [Elasticsearch Introduction](#elasticsearch-introduction)
3. [Setup & Installation](#setup--installation)
4. [Basic Concepts](#basic-concepts)
5. [Python Client](#python-client)
6. [FastAPI Integration](#fastapi-integration)
7. [Search Queries](#search-queries)
8. [Analyzers & Tokenizers](#analyzers--tokenizers)
9. [Synonyms & Autocomplete](#synonyms--autocomplete)
10. [Performance & Best Practices](#performance--best-practices)

---

## Search Kyun Important?

### SQL LIKE vs Full-Text Search

```
SQL LIKE Query:
─────────────────────────────────────────────────────────
SELECT * FROM products WHERE name LIKE '%laptop%'

Problems:
1. ❌ Slow on large data (full table scan)
2. ❌ No relevance ranking
3. ❌ No typo tolerance ("labtop" won't match "laptop")
4. ❌ No synonyms ("notebook" won't match "laptop")
5. ❌ No word stemming ("running" won't match "run")


Elasticsearch Query:
─────────────────────────────────────────────────────────
POST /products/_search
{ "query": { "match": { "name": "laptop" } } }

Advantages:
1. ✅ Fast on large data (inverted index)
2. ✅ Relevance scoring (most relevant first)
3. ✅ Fuzzy matching ("labtop" matches "laptop")
4. ✅ Synonyms ("notebook" can match "laptop")
5. ✅ Stemming ("running" matches "run", "runs", "ran")
```

### When to Use Elasticsearch

```
✅ Good for:
- E-commerce product search
- Blog/article search
- Log analysis
- Auto-complete suggestions
- Full-text search in any field
- Faceted navigation (filter by brand, price, etc.)

❌ Not for:
- Primary database (use PostgreSQL/MongoDB)
- ACID transactions
- Complex joins between data
- Real-time critical data (slight delay possible)
```

---

## Elasticsearch Introduction

### What is Elasticsearch?

```
Elasticsearch = Distributed Search & Analytics Engine

Built on Apache Lucene (search library)
Stores data in JSON format
Uses inverted index for fast search

Components:
┌───────────────────────────────────────────────────┐
│                   Elasticsearch                    │
│                                                    │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │  Node 1  │  │  Node 2  │  │  Node 3  │       │
│   │          │  │          │  │          │       │
│   │ Shard 1  │  │ Shard 2  │  │ Shard 3  │       │
│   │ Replica2 │  │ Replica1 │  │ Replica2 │       │
│   └──────────┘  └──────────┘  └──────────┘       │
│                                                    │
│   Index = Database                                │
│   Document = Row                                  │
│   Field = Column                                  │
│   Shard = Partition                               │
│   Replica = Backup copy                           │
└───────────────────────────────────────────────────┘
```

### How Inverted Index Works

```
Normal Database (Forward Index):
─────────────────────────────────────────────────────────
Doc 1: "The quick brown fox"
Doc 2: "The lazy dog"
Doc 3: "Quick brown dog"

Query "brown" → Scan all docs → Slow!


Inverted Index (Elasticsearch):
─────────────────────────────────────────────────────────
Word     → Documents
─────────────────────
"the"    → [1, 2]
"quick"  → [1, 3]
"brown"  → [1, 3]     ← Instant lookup!
"fox"    → [1]
"lazy"   → [2]
"dog"    → [2, 3]

Query "brown" → Index lookup → Doc 1, 3 → Fast!
```

---

## Setup & Installation

### Docker Setup (Recommended)

```yaml
# docker-compose.yml
version: "3.8"
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false  # Disable for development
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - esdata:/usr/share/elasticsearch/data
    
  kibana:  # Optional: Web UI for Elasticsearch
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  esdata:
```

```bash
# Start Elasticsearch
docker-compose up -d

# Check if running
curl http://localhost:9200
# {
#   "name" : "node-1",
#   "cluster_name" : "docker-cluster",
#   "version" : { "number" : "8.11.0", ... },
#   "tagline" : "You Know, for Search"
# }
```

### Python Dependencies

```bash
pip install elasticsearch
pip install elasticsearch-dsl  # High-level DSL (optional but recommended)
```

---

## Basic Concepts

### Index, Document, Field

```python
# Elasticsearch Terminology:
# 
# Index = Database/Table
# Document = Row/Record
# Field = Column

# Example: products index
{
    "index": "products",
    "document": {
        "_id": "1",
        "name": "MacBook Pro 16",
        "description": "Apple laptop with M3 chip",
        "price": 2499,
        "category": "Electronics",
        "tags": ["laptop", "apple", "macbook"],
        "created_at": "2024-01-15"
    }
}
```

### Mapping (Schema)

```python
# Mapping = Define field types (like database schema)

mapping = {
    "mappings": {
        "properties": {
            "name": {
                "type": "text",           # Full-text searchable
                "analyzer": "standard"
            },
            "name_keyword": {
                "type": "keyword"         # Exact match, sorting, aggregations
            },
            "price": {
                "type": "float"           # Numeric
            },
            "category": {
                "type": "keyword"         # Exact match
            },
            "tags": {
                "type": "keyword"         # Array of exact values
            },
            "description": {
                "type": "text"            # Full-text searchable
            },
            "created_at": {
                "type": "date"            # Date type
            }
        }
    }
}

# Field Types:
# - text: Full-text search (analyzed, tokenized)
# - keyword: Exact match, sorting, aggregations
# - integer/long/float/double: Numbers
# - date: Dates
# - boolean: true/false
# - nested: Nested JSON objects (for complex queries)
# - geo_point: Latitude/longitude
```

---

## Python Client

### Basic Connection

```python
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(
    hosts=["http://localhost:9200"],
    # For secured cluster:
    # basic_auth=("username", "password"),
    # verify_certs=True,
    # ca_certs="/path/to/ca.crt"
)

# Check connection
if es.ping():
    print("Connected to Elasticsearch!")
else:
    print("Connection failed!")

# Get cluster info
info = es.info()
print(f"Cluster: {info['cluster_name']}")
print(f"Version: {info['version']['number']}")
```

### Create Index

```python
# Define index with mapping
index_settings = {
    "settings": {
        "number_of_shards": 1,      # For development
        "number_of_replicas": 0     # No replicas for development
    },
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "standard"},
            "content": {"type": "text"},
            "author": {"type": "keyword"},
            "published_date": {"type": "date"},
            "views": {"type": "integer"}
        }
    }
}

# Create index
if not es.indices.exists(index="articles"):
    es.indices.create(index="articles", body=index_settings)
    print("Index created!")

# Delete index (careful!)
# es.indices.delete(index="articles")
```

### Index Documents (Insert)

```python
# Index single document
doc = {
    "title": "Introduction to FastAPI",
    "content": "FastAPI is a modern web framework for building APIs...",
    "author": "john_doe",
    "published_date": "2024-01-15",
    "views": 1500
}

# Index with auto-generated ID
response = es.index(index="articles", document=doc)
print(f"Document ID: {response['_id']}")

# Index with specific ID
response = es.index(index="articles", id="article-1", document=doc)


# Bulk indexing (for many documents)
from elasticsearch.helpers import bulk

articles = [
    {"_index": "articles", "_id": "1", "_source": {"title": "Article 1", ...}},
    {"_index": "articles", "_id": "2", "_source": {"title": "Article 2", ...}},
    {"_index": "articles", "_id": "3", "_source": {"title": "Article 3", ...}},
]

success, failed = bulk(es, articles)
print(f"Indexed {success} documents, {len(failed)} failed")
```

### Get, Update, Delete

```python
# Get document by ID
doc = es.get(index="articles", id="article-1")
print(doc["_source"])  # The actual document

# Update document
es.update(
    index="articles",
    id="article-1",
    doc={"views": 1600}  # Only update specified fields
)

# Delete document
es.delete(index="articles", id="article-1")
```

---

## FastAPI Integration

### Project Structure

```
app/
├── main.py
├── elasticsearch_client.py
├── models.py
├── schemas.py
├── routes/
│   └── search.py
└── services/
    └── search_service.py
```

### Elasticsearch Client

```python
# elasticsearch_client.py
from elasticsearch import Elasticsearch
from functools import lru_cache

class ElasticsearchClient:
    def __init__(self):
        self.es = Elasticsearch(
            hosts=["http://localhost:9200"]
        )
    
    def get_client(self) -> Elasticsearch:
        return self.es
    
    def create_index_if_not_exists(self, index_name: str, mapping: dict):
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=mapping)


@lru_cache()
def get_es_client() -> ElasticsearchClient:
    return ElasticsearchClient()


# Dependency for FastAPI
def get_elasticsearch():
    client = get_es_client()
    return client.get_client()
```

### Search Service

```python
# services/search_service.py
from elasticsearch import Elasticsearch
from typing import List, Optional

class SearchService:
    def __init__(self, es: Elasticsearch):
        self.es = es
        self.index = "products"
    
    def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        size: int = 10
    ) -> dict:
        """
        Search products with filters
        
        Args:
            query: Search text
            category: Filter by category
            min_price, max_price: Price range
            page, size: Pagination
        """
        
        # Build query
        must = []
        filter_clauses = []
        
        # Text search
        if query:
            must.append({
                "multi_match": {
                    "query": query,
                    "fields": ["name^2", "description"],  # name has 2x weight
                    "fuzziness": "AUTO"  # Typo tolerance
                }
            })
        
        # Category filter
        if category:
            filter_clauses.append({"term": {"category": category}})
        
        # Price range filter
        if min_price or max_price:
            price_range = {}
            if min_price:
                price_range["gte"] = min_price
            if max_price:
                price_range["lte"] = max_price
            filter_clauses.append({"range": {"price": price_range}})
        
        # Build final query
        search_query = {
            "query": {
                "bool": {
                    "must": must if must else [{"match_all": {}}],
                    "filter": filter_clauses
                }
            },
            "from": (page - 1) * size,
            "size": size,
            "highlight": {
                "fields": {
                    "name": {},
                    "description": {}
                }
            }
        }
        
        # Execute search
        response = self.es.search(index=self.index, body=search_query)
        
        # Process results
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        
        products = []
        for hit in hits:
            product = hit["_source"]
            product["_id"] = hit["_id"]
            product["_score"] = hit["_score"]
            product["_highlight"] = hit.get("highlight", {})
            products.append(product)
        
        return {
            "total": total,
            "page": page,
            "size": size,
            "products": products
        }
    
    def index_product(self, product_id: str, product_data: dict):
        """Add/update product in index"""
        self.es.index(
            index=self.index,
            id=product_id,
            document=product_data
        )
    
    def delete_product(self, product_id: str):
        """Remove product from index"""
        self.es.delete(index=self.index, id=product_id)
```

### Search Routes

```python
# routes/search.py
from fastapi import APIRouter, Depends, Query
from elasticsearch import Elasticsearch
from services.search_service import SearchService
from elasticsearch_client import get_elasticsearch

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/products")
async def search_products(
    q: str = Query(default="", description="Search query"),
    category: str = Query(default=None),
    min_price: float = Query(default=None),
    max_price: float = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    es: Elasticsearch = Depends(get_elasticsearch)
):
    """
    Search products with filters
    
    Examples:
    - /search/products?q=laptop
    - /search/products?q=macbook&category=Electronics
    - /search/products?min_price=100&max_price=500
    """
    service = SearchService(es)
    return service.search_products(
        query=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        page=page,
        size=size
    )


@router.get("/suggest")
async def autocomplete(
    q: str = Query(min_length=1, description="Partial search query"),
    es: Elasticsearch = Depends(get_elasticsearch)
):
    """
    Autocomplete suggestions
    
    Example: /search/suggest?q=lap
    Returns: ["laptop", "laptop bag", "laptop stand"]
    """
    query = {
        "suggest": {
            "product-suggest": {
                "prefix": q,
                "completion": {
                    "field": "name_suggest",
                    "size": 5,
                    "fuzzy": {
                        "fuzziness": "AUTO"
                    }
                }
            }
        }
    }
    
    response = es.search(index="products", body=query)
    suggestions = response["suggest"]["product-suggest"][0]["options"]
    
    return [s["text"] for s in suggestions]
```

### Sync with Database

```python
# Sync SQLAlchemy with Elasticsearch

from sqlalchemy.orm import Session
from models import Product
from services.search_service import SearchService

def sync_product_to_elasticsearch(
    db: Session,
    product_id: int,
    search_service: SearchService
):
    """Sync single product to Elasticsearch"""
    product = db.query(Product).get(product_id)
    
    if product:
        search_service.index_product(
            product_id=str(product.id),
            product_data={
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category": product.category,
                "created_at": product.created_at.isoformat()
            }
        )


def full_reindex(db: Session, search_service: SearchService):
    """Reindex all products (for initial setup or recovery)"""
    products = db.query(Product).all()
    
    actions = [
        {
            "_index": "products",
            "_id": str(p.id),
            "_source": {
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "category": p.category
            }
        }
        for p in products
    ]
    
    bulk(search_service.es, actions)


# Call sync after database operations
@app.post("/products")
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    es: Elasticsearch = Depends(get_elasticsearch)
):
    # Save to database
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    
    # Sync to Elasticsearch
    search_service = SearchService(es)
    sync_product_to_elasticsearch(db, db_product.id, search_service)
    
    return db_product
```

---

## Search Queries

### Match Query (Full-text)

```python
# Basic match - analyzes the query and matches
query = {
    "query": {
        "match": {
            "description": "fast api python"
        }
    }
}
# Matches: "FastAPI is a Python framework"
# Because: "fast api python" → ["fast", "api", "python"]


# Match phrase - exact phrase
query = {
    "query": {
        "match_phrase": {
            "description": "fast api"
        }
    }
}
# Only matches if "fast api" appears together in order
```

### Multi-match (Search Multiple Fields)

```python
query = {
    "query": {
        "multi_match": {
            "query": "laptop gaming",
            "fields": ["name^3", "description^2", "tags"],  # Boosting
            "type": "best_fields",  # Use score from best matching field
            "fuzziness": "AUTO"
        }
    }
}

# Field boosting:
# ^3 = 3x importance
# ^2 = 2x importance
# Matching "laptop" in name is more important than in description
```

### Bool Query (Complex Logic)

```python
query = {
    "query": {
        "bool": {
            # All must match (AND)
            "must": [
                {"match": {"category": "Electronics"}}
            ],
            
            # At least one should match (OR, boosts score)
            "should": [
                {"match": {"brand": "Apple"}},
                {"match": {"brand": "Samsung"}}
            ],
            
            # Must not match (NOT)
            "must_not": [
                {"match": {"status": "discontinued"}}
            ],
            
            # Filter (no scoring, faster)
            "filter": [
                {"range": {"price": {"gte": 100, "lte": 1000}}},
                {"term": {"in_stock": True}}
            ]
        }
    }
}
```

### Fuzzy Query (Typo Tolerance)

```python
query = {
    "query": {
        "fuzzy": {
            "name": {
                "value": "laptpo",  # Typo!
                "fuzziness": "AUTO"  # Will match "laptop"
            }
        }
    }
}

# Fuzziness values:
# "AUTO" - Automatic based on term length
# 0, 1, 2 - Exact number of allowed edits
```

### Range Query (Numbers, Dates)

```python
# Price range
query = {
    "query": {
        "range": {
            "price": {
                "gte": 100,   # Greater than or equal
                "lte": 500    # Less than or equal
            }
        }
    }
}

# Date range
query = {
    "query": {
        "range": {
            "created_at": {
                "gte": "2024-01-01",
                "lte": "now"  # Current time
            }
        }
    }
}
```

### Aggregations (Analytics)

```python
query = {
    "size": 0,  # Don't return documents, only aggregations
    "aggs": {
        # Count by category
        "categories": {
            "terms": {
                "field": "category",
                "size": 10
            }
        },
        
        # Price statistics
        "price_stats": {
            "stats": {
                "field": "price"
            }
        },
        
        # Price ranges (buckets)
        "price_ranges": {
            "range": {
                "field": "price",
                "ranges": [
                    {"to": 100},
                    {"from": 100, "to": 500},
                    {"from": 500}
                ]
            }
        }
    }
}

# Response:
# {
#   "aggregations": {
#     "categories": {
#       "buckets": [
#         {"key": "Electronics", "doc_count": 150},
#         {"key": "Clothing", "doc_count": 75}
#       ]
#     },
#     "price_stats": {
#       "count": 1000,
#       "min": 9.99,
#       "max": 2499.00,
#       "avg": 299.50
#     }
#   }
# }
```

---

## Analyzers & Tokenizers

### What is an Analyzer?

```
Analyzer = Tokenizer + Token Filters

Text: "The QUICK brown Fox jumps!"
          ↓
Tokenizer: ["The", "QUICK", "brown", "Fox", "jumps"]
          ↓
Lowercase Filter: ["the", "quick", "brown", "fox", "jumps"]
          ↓
Stop Words Filter: ["quick", "brown", "fox", "jumps"]
          ↓
Stored in Index
```

### Built-in Analyzers

```python
# Standard analyzer (default)
# - Splits on whitespace and punctuation
# - Lowercases
# "The Quick-Brown FOX!" → ["the", "quick", "brown", "fox"]

# Simple analyzer
# - Splits on non-letters
# - Lowercases
# "2Fast2Furious" → ["fast", "furious"]

# Whitespace analyzer
# - Only splits on whitespace
# "Quick Brown FOX" → ["Quick", "Brown", "FOX"]

# Language analyzers
# - English, German, Hindi, etc.
# - Stemming: "running" → "run"
# - Stop words removal
```

### Custom Analyzer

```python
index_settings = {
    "settings": {
        "analysis": {
            "analyzer": {
                "my_custom_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stemmer",
                        "my_stop_words"
                    ]
                }
            },
            "filter": {
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "my_stop_words": {
                    "type": "stop",
                    "stopwords": ["the", "a", "an", "and", "or"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "my_custom_analyzer"
            }
        }
    }
}
```

---

## Synonyms & Autocomplete

### Synonyms

```python
# Index with synonyms
index_settings = {
    "settings": {
        "analysis": {
            "filter": {
                "my_synonyms": {
                    "type": "synonym",
                    "synonyms": [
                        "laptop, notebook, portable computer",
                        "phone, mobile, smartphone",
                        "tv, television, telly"
                    ]
                }
            },
            "analyzer": {
                "search_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "my_synonyms"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "name": {
                "type": "text",
                "analyzer": "standard",
                "search_analyzer": "search_analyzer"  # Use synonyms for search
            }
        }
    }
}

# Now searching "notebook" will also match "laptop"!
```

### Autocomplete (Completion Suggester)

```python
# Index with completion field
index_settings = {
    "mappings": {
        "properties": {
            "name": {"type": "text"},
            "name_suggest": {
                "type": "completion",  # Special type for autocomplete
                "analyzer": "standard"
            }
        }
    }
}

# Index document
doc = {
    "name": "MacBook Pro 16",
    "name_suggest": {
        "input": ["MacBook", "MacBook Pro", "MacBook Pro 16", "Apple Laptop"],
        "weight": 10  # Higher weight = higher priority
    }
}
es.index(index="products", document=doc)


# Search suggestions
query = {
    "suggest": {
        "product-suggest": {
            "prefix": "mac",  # User typed "mac"
            "completion": {
                "field": "name_suggest",
                "size": 5,
                "fuzzy": {
                    "fuzziness": "AUTO"
                }
            }
        }
    }
}

# Returns: ["MacBook", "MacBook Pro", "MacBook Pro 16"]
```

### Search-as-you-type

```python
# Better autocomplete for partial matching
index_settings = {
    "mappings": {
        "properties": {
            "name": {
                "type": "search_as_you_type"
            }
        }
    }
}

# Query
query = {
    "query": {
        "multi_match": {
            "query": "macbo",  # Partial input
            "type": "bool_prefix",
            "fields": [
                "name",
                "name._2gram",
                "name._3gram"
            ]
        }
    }
}
```

---

## Performance & Best Practices

### 1. Use Filters for Non-Scoring Queries

```python
# ❌ Slow - match in must (calculates score)
{
    "query": {
        "bool": {
            "must": [
                {"term": {"status": "active"}}  # Scoring not needed
            ]
        }
    }
}

# ✅ Fast - filter clause (no scoring, cacheable)
{
    "query": {
        "bool": {
            "filter": [
                {"term": {"status": "active"}}
            ]
        }
    }
}
```

### 2. Limit Fields Returned

```python
# Return only needed fields
query = {
    "query": {"match_all": {}},
    "_source": ["name", "price", "category"]  # Only these fields
}

# Or exclude large fields
query = {
    "query": {"match_all": {}},
    "_source": {
        "excludes": ["description", "content"]
    }
}
```

### 3. Use Pagination Properly

```python
# ❌ Don't use from + size for deep pagination
# Elasticsearch loads all docs up to from + size

# For deep pagination, use search_after
query = {
    "size": 10,
    "query": {"match_all": {}},
    "sort": [{"created_at": "desc"}, {"_id": "asc"}],
    "search_after": ["2024-01-15", "abc123"]  # Last doc's sort values
}
```

### 4. Bulk Operations

```python
from elasticsearch.helpers import bulk

# ✅ Bulk indexing
actions = [
    {"_index": "products", "_id": str(p.id), "_source": p.dict()}
    for p in products
]
bulk(es, actions, chunk_size=500)

# ✅ Bulk delete
actions = [
    {"_op_type": "delete", "_index": "products", "_id": str(id)}
    for id in ids_to_delete
]
bulk(es, actions)
```

### 5. Index Settings for Production

```python
production_settings = {
    "settings": {
        "number_of_shards": 3,     # Distribute data
        "number_of_replicas": 1,   # High availability
        "refresh_interval": "30s", # Less frequent refresh
        "index.mapping.total_fields.limit": 1000
    }
}
```

---

## Practice Exercises

### Exercise 1: Product Search
```python
# Build product search with:
# - Full-text search in name and description
# - Filter by category, price range
# - Sort by relevance/price/date
# - Highlight matches
```

### Exercise 2: Autocomplete
```python
# Build autocomplete:
# - Return top 5 suggestions
# - Handle typos
# - Show in dropdown as user types
```

### Exercise 3: Analytics Dashboard
```python
# Build analytics:
# - Count products by category
# - Average price per category
# - Top 10 most searched terms
```

---

## Quick Reference

```python
# Connect
from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Create index
es.indices.create(index="products", body=mapping)

# Index document
es.index(index="products", id="1", document=doc)

# Search
es.search(index="products", body=query)

# Common queries:
# match: Full-text search
# term: Exact match
# bool: Combine queries
# range: Numeric/date range

# Aggregations:
# terms: Group by field
# stats: Min/max/avg/sum
# range: Bucket by ranges
```

---

> **Pro Tip**: "Elasticsearch sirf search ke liye use karo - primary database PostgreSQL hi rakho!" 🔍
