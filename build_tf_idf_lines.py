
from tfidf_search import TfidfSearcher 

searcher = TfidfSearcher(['data/2020.txt', 'data/2019.txt', 'data/2018.txt'])
# print (searcher.all_titles[0])

searcher.save()
