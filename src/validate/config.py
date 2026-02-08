serpapi_config = {
    "env": "SERPAPI_API_KEY",
    
    "base_url": "https://serpapi.com/search",
    
    "default_params": {
        "engine": "google_trends",
        "hl": "en",         
        "geo": "", # empty = worldwide
        "date": "today 3-m",  
        "tz": "360", # central time
    },
    
    # Rate limiting
    "requests_per_second": 2,  
    "batch_size": 5,           
}

# Validation thresholds
validation_config = {
    "interest_threshold": 15.0,      
    "related_threshold": 10.0,       
    "max_related_per_query": 5,     
    "min_data_points": 3, # data points required for valid trend
}
