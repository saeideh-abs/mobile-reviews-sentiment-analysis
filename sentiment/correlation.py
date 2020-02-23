import scipy.stats

def spearman_correlation(list1, list2):
    list1_ranking = []
    list2_ranking = []
    
    for item in list1:
        if item not in list2:
            list2.append(item)
    for item in list2:
        if item not in list1:
            list1.append(item)
    print(list1)
    print(list2)
    for index, item in enumerate(list1):
        list1_ranking.append(index + 1)
        list2_rank = list2.index(item) + 1
        list2_ranking.append(list2_rank)
    print("list1 ranks:", list1_ranking)
    print("list2 ranks:", list2_ranking)
    correlation = scipy.stats.spearmanr(list1_ranking, list2_ranking)[0]
    return correlation