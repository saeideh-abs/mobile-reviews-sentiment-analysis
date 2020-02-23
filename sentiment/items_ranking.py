# this function get lists of items and its labels(scores) and calculate
# final score for each item. then sort items according to its scores
def ranking(items, labels):
    points = {}
    count = {} 
    weighted_order = {}
    total = 0
    for index, item in enumerate(items):
        #print("index:", index, "label:", labels[index])
        if item not in points:
            points[item] = 0
            count[item] = [0, 0, 0, 0] #negative, neutral, positive, total
            #print("points[item] = 0")
        if labels[index] == 1 or labels[index] == '1':
            points[item] += 1
            count[item][2] += 1
            count[item][3] += 1
            #print("score increased", item, "count:", count[item])
        elif labels[index] == 0 or labels[index] == '0':
            points[item] -= 1
            count[item][0] += 1
            count[item][3] += 1
            #print("score decreased", item, "count:", count[item])
        else:
            count[item][1] += 1
            count[item][3] += 1
            #print("neutral", "count:", item, count[item])
    
    for index, item in count.items():
        #print(item, item[3], type(item[3]))
        total += item[3]
    for index, item in points.items():
       weighted_order[index] = (count[index][3]/total)*(item/(count[index][3]-count[index][1]+0.000000001)) #
    sorted_points = [(item, weighted_order[item]) for item in sorted(weighted_order, key=weighted_order.get, reverse = True)]
    #sorted_points = [(item, points[item]) for item in sorted(points, key=points.get, reverse = True)]
    return [sorted_points, count, total]
