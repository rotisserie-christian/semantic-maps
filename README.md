# Search Profiler 

Creates & validates search terms specific to the behaviour of a given user profile. It uses heuristics derived from research on user behaviour to construct an LLM prompt, and outputs the result in JSON format. 

It uses Replicate to make it easy to experiment with different models. You can then validate these search terms against Google Trends data via SerpAPI. 

> [!WARNING]  
> Pricing on Replicate is token-based and varies by model. SerpAPI is also usage based, and this script can very easily burn through API credits. I would recommend using small sets of search terms until you're familiar with using this script. 

> [!TIP]
> Adjust max_tokens in src/config.py to limit the number of generated terms. Usually ~100 tokens = 1 search term. SerpAPI will not be called unless you run the --validate flag, more info is below. 

## Set up

Clone the repo:
```bash
git clone https://github.com/rotisserie-christian/search-profiler
```

Install dependencies (Python 3.10):
```bash
pip install -r requirements.txt
```

Add replicate token:
```bash
export REPLICATE_API_TOKEN ="token" 
```

Add SerpAPI token:
```bash
export SERPAPI_API_KEY ="token" 
```

Fill out the user profile in **`src/config.py`** and then run the script:
```bash
python main.py 
```

## Multiple runs 

This will query the LLM x times, collect all unique search terms, and consolidate the output
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

## Manual pruning 

I would recommend pruning any slop generations from the JSON output before validating. This will conserve API credits. 

This needs to be done to the JSON file in particular, since this is the format used to call SerpAPI. The TXT and CSV outputs are meant for quick readability and export, and are not used in the actual script itself. 

## Validation

Run the **`--validate`** flag to filter out terms with low interest and discover related queries that are currently trending.

This flag will call SerpAPI instead of Replicate. You will need to include the JSON file as an argument.

```bash
python main.py --validate output/searchterms1.json
```

> [!NOTE]  
> It has to be the JSON file, not the CSV or TXT file.

## Dependencies 
- **`Replicate`** - LLM API
- **`sentence-transformers`** - semantic clustering
- **`scikit-learn`** - cosine similarity
- **`numpy`** - numerical operations
- **`requests`** - HTTP requests
