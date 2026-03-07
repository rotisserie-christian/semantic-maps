# Search Profiler 

Toolkit for researching search terms specific to the behaviour of a given user profile. 

The point is to explore as many potential branches of search intent as possible, either through the LLM workflow, or by your own anlaysis, or some combination of the two, and then validate against Google Trends data.

It's meant to help fill in the gaps you may have missed, and compliment your existing strategy. It's not supposed to be an agentic system or something that just gives you all the answers. 

> [!WARNING]  
> Pricing on Replicate is token-based and varies by model. SerpAPI is also usage based, and this script can very easily burn through API credits. I would recommend using small sets of search terms until you're familiar with using this script. 

> [!TIP]
> Adjust max_tokens in src/config.py to limit the number of generated terms. Usually ~100 tokens = 1 search term.

## Contents
- [Set up](##set-up)
- [Multiple runs](##multiple-runs)
- [Manual pruning](##manual-pruning)
- [Manual addition](##manual-addition)
- [Explore related terms](##explore-related-terms)
- [Validation](##validation)
- [Time Series](##time-series)
- [Slope](##slope)
- [Dependencies](##dependencies)

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

This will check if it exists, if it doesn't, it will use `sentence-transformers` to find the best matching cluster and add the query to it. 

## Explore related terms 

> [!WARNING]  
> This step can use a lot of serpAPI credits. It also tends to return queries that are less relevant to the specific search intent of the given user profile. However, it can sometimes return highly valuable queries. Just be aware that this is an optional step with a slot machine mechanic baked into it. 

This will call serpAPI to retrieve related queries for each search term if they exist, and add them to the appropriate cluster. It takes in a searchtermsN.json file as an argument and writes the new terms to the same file.

```bash
python main.py --explore output/searchtermsN.json
```

## Validation

Run the **`--validate`** flag to call SerpAPI, creating a new JSON file containing search interest data for each term. It will omit any terms with 0 data and write the result to `/output/validatedtermsN.json`

```bash
python main.py --validate output/searchtermsN.json
```

> [!NOTE]  
> It has to be the JSON file, not the CSV or TXT file.

## Time Series 

Run the **`--timeseries`** flag to get search interest over time for each term. It takes in a validatedtermsN.json file and writes the result to `/output/timeseries/timeseriesN.json`
```bash
python main.py --timeseries output/validatedtermsN.json
```

The time period is set in **`src/validate/config.py`** 

It uses 3-month by default since this is the longest period that still provides daily data. If you want to use a different period you may need to modify the script. 

## Slope

Run the **`--slope`** flag with the `timeseriesN.json` file as an argument to calculate the rate of change for each search term, and write the result to `/output/slope/timeseriesslopeN.json`

```bash
python main.py --slope output/timeseries/timeseriesN.json
```

The output will contain `slope` as a single value for each query, along with `avg_interest`, `max_interest`, and `cluster` 

## Dependencies 
- **`Replicate`** - LLM API
- **`sentence-transformers`** - semantic clustering
- **`scikit-learn`** - cosine similarity
- **`numpy`** - numerical operations
- **`requests`** - HTTP requests
