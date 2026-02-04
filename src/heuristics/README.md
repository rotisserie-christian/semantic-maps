### Heuristics
- **`query_length.py`** - Age = tendency for longer vs shorter queries (younger = longer) <sup>1,6</sup>.
- **`complexity.py`** - Age + domain expertise = how elaborate the initial query is <sup>2,3,7</sup>.
- **`reformulation.py`** - Domain expertise + age = sticks to initial terms vs strategic reformulation / new keywords <sup>2,4,5</sup>.
- **`specificity.py`** - Age + prior task knowledge = vague vs specific phrasing <sup>2,6</sup>.
- **`patience.py`** - Age + cognitive flexibility = time per SERP, evaluation vs quick adjustment <sup>3,7</sup>.
- **`word_choice.py`** - Age + expertise = vocabulary style (confident/casual vs formal, jargon vs lay terms) <sup>6</sup>.

### Aggregator
- **`prompts.py`** - Imports all heuristics and returns prompts for `assemble_prompts.py`

### References
1. <small>Yom-Tov E. Demographic differences in search engine use with implications for cohort selection. *Information Retrieval Journal* 22, 570–580 (2019). https://link.springer.com/article/10.1007/s10791-018-09349-2</small>  

2. <small>Sanchiz M. et al. Age-related differences in web information search. *Computers in Human Behavior* (2017). https://www.sciencedirect.com/science/article/abs/pii/S0747563217301127</small>  

3. <small>Chevalier A. et al. Strategy and accuracy during information search on the Web: effects of age and complexity of the search questions. *Research in Psychology* (2015). https://www.researchgate.net/publication/280920763_Strategy_and_accuracy_during_information_search_on_the_Web_Effects_of_age_and_complexity_of_the_search_questions</small>

4. <small>Zhang X., Anghelescu H.G.B. & Yuan X. Domain knowledge, search behaviour, and search effectiveness of engineering and science students. *Information Research* 10(2) paper 217 (2005). https://informationr.net/ir/10-2/paper217.html</small>

5. <small>Kalyani R. Understanding user search processes across varying cognitive levels. *arXiv* (2019). https://arxiv.org/abs/1909.04773</small>  

6. <small>UserTesting. How different age demographics search the internet (2023). https://www.usertesting.com/blog/how-different-age-demographics-search-the-internet</small>  

7. <small>Chevalier A. et al. Age-related differences in search behavior and perceived search difficulty. *Computers in Human Behavior* (2015). https://www.sciencedirect.com/science/article/abs/pii/S0306457315000552</small>  

8. <small>Hargittai E. & Hinnant A. Digital inequality: differences in young adults’ use of the Internet. *Journal of Computer-Mediated Communication* 12(3), 778–797 (2007). https://academic.oup.com/jcmc/article/12/3/778/4582966</small>  
