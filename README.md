## Search Profiler 

Creates search terms specific to the behaviour of a given user profile. It uses heuristics derived from research on user behaviour to construct an LLM prompt, and outputs the result in CSV format. 

It uses Replicate to make it easy to experiment with different models. Keep in mind that pricing is token-based and varies by model, and a single search term will usually be around 100 tokens. The default is set to Deepseek v3, which currently costs around $3/million output tokens. 

## How to use it

Clone the repo:
```bash
git clone https://github.com/rotisserie-christian/search-profiler
```

Install dependencies (Python 3.10):
```bash
pip install -r requirements.txt
```

Add replicate token (linux):
```bash
export REPLICATE_API_TOKEN="token"
```

Add replicate token (powershell):
```bash
$env:REPLICATE_API_TOKEN = "token"
```

Fill out the user profile in **`config.py`** and then run the script:
```bash
python main.py 
```

## Dependencies 
- **`Replicate`** - LLM API