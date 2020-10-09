

from linkage_search import LinkageSearcher 

searcher = LinkageSearcher(['data/2020.txt', 'data/2019.txt', 'data/2018.txt'])
# print (searcher.all_titles[0])

searcher.save()
