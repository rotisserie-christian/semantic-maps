### src
- **`/heuristics`** - Logic for inferring search behaviour 
- **`/llm`** - Prompt + output file construction, querying the LLM
- **`/output`** - CSV outputs
- **`/ui`** - Optional TUI feature 
- **`/utils`** - Helper functions 
- **`config.py`** - User profile and llm settings 

### Flow
```
User profile  ->  Prompt construction  ->  LLM  ->  CSV 
```