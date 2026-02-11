# Search Profiler 

Toolkit for researching search terms specific to the behaviour of a given user profile. It uses heuristics derived from research on user behaviour to construct an LLM prompt, and outputs the result in JSON format. 

It uses Replicate to make it easy to experiment with different models. You can then validate these search terms against Google Trends data via SerpAPI. 

> [!WARNING]  
> Pricing on Replicate is token-based and varies by model. SerpAPI is also usage based, and this script can very easily burn through API credits. I would recommend using small sets of search terms until you're familiar with using this script. 

> [!TIP]
> Adjust max_tokens in src/config.py to limit the number of generated terms. Usually ~100 tokens = 1 search term.

## Set up

Clone the repo:
```bash
git clone https://github.com/rotisserie-christian/search-profiler
```

Install dependencies (Python 3.10):
```bash
pip install -r requirements.txt
```

Add your **`REPLICATE_API_TOKEN`** and **`SERPAPI_API_KEY`**, fill out the user profile in **`src/config.py`** and then run the script:
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

## Manual addition

You can also add your own queries to the JSON file

cd into **`src/utils`** and run:
```bash
python add_query.py searchtermsN.json
```

This will check if it exists, if it doesn't, it will use sentence-transformers to find the best matching cluster and add the query to it. 

## Validation

Run the **`--validate`** flag to get a new JSON file containing search interest data for each term. 

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
