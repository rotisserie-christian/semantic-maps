# Semantic Maps

This is my market research toolkit, it can be used for a few different things:

#### Brainstorm
Generate a preliminary list of keywords based on the search behaviour of a given user persona

#### Validation 
Validates a set of keywords against Google Trends

#### Reviews
Pulls Google reviews from businesses in a given market, semantically clusters the feedback, and sorts them by ratings

## Contents
- [Set up](#set-up)
- [Keyword Brainstorming](#keyword-brainstorming)
  - [Multiple Runs](#multiple-runs)
  - [Manual Pruning](#manual-pruning)
  - [Manual Addition](#manual-addition)
  - [Explore Related Terms](#explore-related-terms)
- [Trends Validation](#trends-validation)
  - [Validation](#validation)
  - [Normalization (Anchor Terms)](#normalization-anchor-terms)
- [Google Maps Reviews](#google-maps-reviews)
  - [Live Fetch](#live-fetch)
  - [Cached Replay](#cached-replay)
- [Dependencies](#dependencies)

## Set up

Clone the repo:

```bash
git clone https://github.com/rotisserie-christian/search-profiler
```

Install dependencies (Python 3.10):

```bash
pip install -r requirements.txt
```

Add your **`REPLICATE_API_TOKEN`** and **`SERPAPI_API_KEY`**, fill out the user profile in **`src/config.py`**

## Keyword Brainstorming

### Multiple runs 

This will query the LLM x times, collect all unique search terms, and consolidate the output

> [!TIP]
> Adjust max_tokens in src/config.py to limit the number of generated terms. Usually ~100 tokens = 1 search term.

```bash
python main.py --runs x
```

This also consolidates the cluster titles based on semantic similarity

Adjust the similarity threshold (default 0.75):

```bash
python main.py --runs x --threshold y
```

> [!WARNING]  
> This creates a lot more output tokens. This is why I set the default model to Deepseek. A high number of runs with a more expensive model can create a massive bill very quickly. 

### Head vs long-tail (`--mode`)

Google Trends only has reliable volume for short, head-style queries. As of right now, there is no system here for validating long-tail terms, but you can still generate them if you want to. The `--mode` flag controls which heuristics drive generation:

- **`head`** - short, high-volume terms (uses `word_choice`, `reformulation`); best for Trends validation
- **`tail`** - long-tail persona terms (uses `query_length`, `complexity`, `specificity`); best for intent mapping / SEO
- **`both`** - all heuristics (default)

```bash
python main.py --runs x --mode head
```

### Manual pruning 

I would recommend pruning any slop generations from the JSON output before validating. This will conserve API credits. 

This needs to be done to the JSON file in particular, since this is the format used to call SerpAPI. The TXT and CSV outputs are meant for quick readability and export, and are not used in the actual script itself. 

### Manual addition

You can also add your own queries to the JSON file

cd into **`src/utils`** and run:

```bash
python add_query.py searchtermsN.json
```

This will check if it exists, if it doesn't, it will use `sentence-transformers` to find the best matching cluster and add the query to it. 

### Explore related terms 

> [!WARNING]  
> This step can use a lot of serpAPI credits. It also tends to return queries that are less relevant to the specific search intent of the given user profile. However, it can sometimes return highly valuable queries. Just be aware that this is an optional step with a slot machine mechanic baked into it. 

This will call serpAPI to retrieve related queries for each search term if they exist, and add them to the appropriate cluster. It takes in a searchtermsN.json file as an argument and writes the new terms to the same file.

```bash
python main.py --explore output/searchtermsN.json
```

## Trends Validation

### Validation

Run the **`--validate`** flag to call SerpAPI, creating a new JSON file containing search interest data for each term. It will omit any terms with 0 data and write the result to `/output/validatedtermsN.json`

```bash
python main.py --validate output/searchtermsN.json --anchor "your anchor term"
```

> [!NOTE]  
> It has to be the JSON file, not the CSV or TXT file.

### Normalization (Anchor Terms)

Google Trends data is relative (0-100) and specific to the terms in a single query. To compare hundreds of terms across different batches, you **must** use an anchor term.

By passing the `--anchor` flag, the script:
1. Includes your anchor in every API batch.
2. Calculates a "Batch Multiplier" based on the anchor's performance.
3. Rebases all other terms in that batch against a global reference scale.

**Without an anchor, high-volume and low-volume terms will look identical on a chart if they are in different batches.**

## Google Maps Reviews

Semantically cluster and analyze business reviews from Google Maps to surface recurring customer feedback themes, strengths, and weaknesses.

### Live Fetch
Query Google Maps for businesses in a market, retrieve their highest/lowest reviews, and run LLM semantic clustering:
```bash
python main.py --reviews --query "<business> in <location>" --type "<business_type>"
```

### Cached Replay
Re-run LLM semantic clustering and analytical metric passes locally using previously fetched raw JSON to save API credits:
```bash
python main.py --reviews --query "any-label" --load-raw output/raw_reviews/latest_fetch.json
```

## Dependencies 
- **`Replicate`** - LLM API
- **`sentence-transformers`** - semantic clustering
- **`scikit-learn`** - cosine similarity
- **`numpy`** - numerical operations
- **`requests`** - HTTP requests
