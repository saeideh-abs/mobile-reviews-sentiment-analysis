# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 12:09:50 2019

@author: saeideh abbaszadeh

first accuracy: 0.43 (with considdering pos, neg, neutral labels in result labels)
second accuracy: 0.68 (with considdering just pos, neg labels in result labels and ingnoring neutral class )
third accuracy: 0.63 (with changing lexicon and considering pos, neg and neutral tags) 
forth accuracy: 0.663 (some additional words was added)
fifth accuracy: 0.669 (list of negative verbs was added)
"""
import json
from nltk.metrics.scores import (accuracy)
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score 
import items_ranking
import correlation

########## determine each text polarity using lexicon based approach ##########
def sentence_polarity(comment):
  score = 0
  words = comment.split()
  
  for index, word in enumerate(words):
      if word in positive_words:
          score += 1
      if word in negative_words:
          score += -1
      if word in negative_verbs:
          if word not in neg_verbs:
              neg_verbs[word] = [[],[]]
          for i in range(2): #setting range to 2 gives best accuracy
              if index-i >= 0 :
                  if words[index-i] in positive_words:
                      score += -2
                      neg_verbs[word][0].append(words[index-i])               
                  if words[index-i] in negative_words:
                      score += 2
                      neg_verbs[word][1].append(words[index-i]) 
  if score >= 1:
      label = 1
  elif score == 0:
      label = 2
  else:
      label = 0
  return label

############################ variables ########################################
comments = []
real_labels = []
result_labels = []
mobileir_brands = []
mobileir_comments = []
mobileir_labels = []
popular_brands_names = []
neg_verbs = {}
########################### read and load neccessary data #####################
with open('../dataset/mobile.ir.final.json', encoding="utf8") as json_file:
    mobile_ir = json.load(json_file)
mobile_brands = open("../dataset/mobile_brands.txt", encoding="utf8").read().split('\n')

dataset = open("../dataset/mobile_digikala.csv", encoding="utf8").read().split('\n') #read dataset
dataset = dataset[1:] #remove csv headers

positive_words = open("../dataset/dataheart_lexicon/positive_words.txt", encoding="utf8").read().split('\n') 
negative_words = open("../dataset/dataheart_lexicon/negative_words.txt", encoding="utf8").read().split('\n') 
negative_verbs = open("../dataset/dataheart_lexicon/negative_verbs.txt", encoding="utf8").read().split('\n') 

digikala_ranking = open("../dataset/digikala_ranking.txt", encoding="utf8").read().split('\n')
cafebazar_ranking = open("../dataset/cafebazar_ranking.txt", encoding="utf8").read().split('\n')
gs_statcounter_ranking = open("../dataset/gs.statcounter_ranking.txt", encoding="utf8").read().split('\n')

negative_verbs_detail = open("founded_negative_verbs.txt","w", encoding="utf8")
negative_verbs_detail.write("**************** digikala dataset negative verbs *****************\n") 

for comment in dataset[:len(dataset)]:
    #print(comment)
    comment = comment.split(',')
    comments.append(comment[1])
    real_labels.append(int(comment[0]))
    sent_polarity = sentence_polarity(comment[1])
    result_labels.append(sent_polarity)
    
for key, item in neg_verbs.items():
     neg_count = {}
     pos_count = {}
     negative_verbs_detail.write("\n -------------------------------------------")
     negative_verbs_detail.write('\n' + str(key) + '\n')
     #negative_verbs_detail.write(str(neg_verbs[key][0]) + '\n')
     negative_verbs_detail.write("negative adjectives:\n")
     #negative_verbs_detail.write(str(neg_verbs[key][1]) + '\n')
     if neg_verbs[key][1] != []:
         for adj in neg_verbs[key][1]:
             if adj not in neg_count:
                 neg_count[adj] = 1
             else:
                 neg_count[adj] += 1
         for index, item in neg_count.items():
            negative_verbs_detail.write(index + ': ' + str(item) + '\n')
        
     negative_verbs_detail.write("positive adjectives:\n")
     
     if neg_verbs[key][0] != []:
         for adj in neg_verbs[key][0]:
             if adj not in pos_count:
                 pos_count[adj] = 1
             else:
                 pos_count[adj] += 1
     for key, item in pos_count.items():
        negative_verbs_detail.write(key + ': ' + str(item) + '\n')
################################## Evaluation #################################
accuracy = accuracy(real_labels, result_labels)
print("accuracy", accuracy)
precision = precision_score(real_labels, result_labels, labels=None, average='weighted')
print("precision:", precision)
recall = recall_score(real_labels, result_labels, labels=None, average='weighted')
print("recall:", recall)

#calculate accuracy without considering neutral labels
count = 0
total = 0
for index in range(len(result_labels)):
    if result_labels[index] != 2:
        total += 1 
        if result_labels[index] == real_labels[index]:
            count += 1
            
print("my accuracy", count/total)
##################### determine the most popular mobile brand #################
print("*************** determine the most popular mobile brand **************")
negative_verbs_detail.write("**************** mobile.ir comments negative verbs *****************\n") 
neg_verbs = {}
for obj in mobile_ir:
    flag = 0
    for index, brand in enumerate(mobile_brands):
        if brand in obj['brand_model']:
            flag += 1
            if flag == 1 :
                mobileir_brands.append(brand)
                mobileir_comments.append(obj['comment'])
                label = sentence_polarity(obj['comment'])
                mobileir_labels.append(label)

for key, item in neg_verbs.items():
     neg_count = {}
     pos_count = {}
     negative_verbs_detail.write("\n -------------------------------------------")
     negative_verbs_detail.write('\n' + str(key) + '\n')
     #negative_verbs_detail.write(str(neg_verbs[key][0]) + '\n')
     negative_verbs_detail.write("negative adjectives:\n")
     #negative_verbs_detail.write(str(neg_verbs[key][1]) + '\n')
     for adj in neg_verbs[key][1]:
         if adj not in neg_count:
             neg_count[adj] = 1
         else:
             neg_count[adj] += 1
     for index, item in neg_count.items():
        negative_verbs_detail.write(index + ': ' + str(item) + '\n') 
        
     negative_verbs_detail.write("positive adjectives:\n")
     for adj in neg_verbs[key][0]:
         if adj not in pos_count:
             pos_count[adj] = 1
         else:
             pos_count[adj] += 1
     for key, item in pos_count.items():
        negative_verbs_detail.write(key + ': ' + str(item) + '\n')

brands_ranking = items_ranking.ranking(mobileir_brands, mobileir_labels)   
popular_brands = brands_ranking[0]
details = brands_ranking[1]

for phone in popular_brands:
    print(phone)
    popular_brands_names.append(phone[0])

for key, item in details.items():
    print("********************", key, "*****************")
    print("number of negatives:", item[0])
    print("number of neutrals:", item[1])
    print("number of positives:", item[2])
    print("total:", item[3])

######################### calculate spearman correlation ######################
print("***************** calculate spearman correlation  ********************")
print("cafebazar correlation:", correlation.spearman_correlation(cafebazar_ranking, popular_brands_names))
print("**********************************************************************")
print("gs statcounter correlation:", correlation.spearman_correlation(gs_statcounter_ranking, popular_brands_names))
print("**********************************************************************")
print("digikala correlation:", correlation.spearman_correlation(digikala_ranking, popular_brands_names))

negative_verbs_detail.close()
print("end :)")     

