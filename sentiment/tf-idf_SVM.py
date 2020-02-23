# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 12:09:50 2019

@author: saeideh abbaszadeh
"""
import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection  import GridSearchCV
from sklearn import svm
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score 
from sklearn.linear_model import LogisticRegression
import items_ranking
import correlation

train_comments = []
test_comments = []
train_labels = []
test_labels = []
mobileir_brands = []
mobileir_comments = []
popular_brands_names = []

#reading dataset
with open('../dataset/mobile.ir.final.json', encoding="utf8") as json_file:
    mobile_ir = json.load(json_file)
mobile_brands = open("../dataset/mobile_brands.txt", encoding="utf8").read().split('\n')
dataset = open("../dataset/mobile_digikala.csv", encoding="utf8").read().split('\n')
dataset = dataset[1:] #remove csv headers
train_data, test_data = train_test_split(dataset, test_size = 0.1)
train_len = len(train_data) #2453
test_len = len(test_data) #273

digikala_ranking = open("../dataset/digikala_ranking.txt", encoding="utf8").read().split('\n')
cafebazar_ranking = open("../dataset/cafebazar_ranking.txt", encoding="utf8").read().split('\n')
gs_statcounter_ranking = open("../dataset/gs.statcounter_ranking.txt", encoding="utf8").read().split('\n')

    
for comment in train_data:
    comment = comment.split(',')
    train_comments.append(comment[1])
    train_labels.append(comment[0])
for comment in test_data:
    comment = comment.split(',')
    test_comments.append(comment[1])
    test_labels.append(comment[0])

################################## SVM training ###############################
# Create feature vectors using tf-idf
vectorizer = TfidfVectorizer(min_df = 5, max_df = 0.8, sublinear_tf = True, use_idf = True)
train_vectors = vectorizer.fit_transform(train_comments)
test_vectors = vectorizer.transform(test_comments)
#feature_names = vectorizer.get_feature_names()
#res = dict(zip(vectorizer.get_feature_names(), mutual_info_classif(tf_idf_vectors, real_labels, discrete_features=True)))
#for item in list(res)[:200]:
    #print(item)

# Perform classification with SVM, kernel=linear
param_grid = {'C': [0.01, 0.1, 1, 10, 100], 'kernel': ['rbf', 'linear']}
lsvm = GridSearchCV(svm.SVC(class_weight='balanced', probability=True), param_grid)
lsvm.fit(train_vectors, train_labels)
print("************************** best estimator **********************")
print("best estimator", lsvm.best_estimator_)
predicted_labels = lsvm.predict(test_vectors)
probability = lsvm.predict_proba(test_vectors)
score = lsvm.score(test_vectors, test_labels)
print("****************************************************************")
print("svm score:", score)
precision_pos = precision_score(test_labels, predicted_labels, labels=None, pos_label='1', average='binary')
print("precision of positives:", precision_pos)
recall_pos = recall_score(test_labels, predicted_labels, labels=None, pos_label='1', average='binary')
print("recall of positives:", recall_pos)

precision_neg = precision_score(test_labels, predicted_labels, labels=None, pos_label='0', average='binary')
print("precision of negatives:", precision_neg)
recall_neg = recall_score(test_labels, predicted_labels, labels=None, pos_label='0', average='binary')
print("recall of negatives:", recall_neg)

################################ Logestic Regression ##########################
# perform classification with logestic regression
lrg = LogisticRegression()
lrg.fit(train_vectors, train_labels)
score = lrg.score(test_vectors, test_labels)
print("logreg score:", score)
print("****************************************************************")
##################### determine the most popular mobile brand #################
print("**************** determine the most popular mobile brand **************")
for obj in mobile_ir:
    flag = 0
    for index, brand in enumerate(mobile_brands):
        if brand in obj['brand_model']:
            flag += 1
            if flag == 1 :
                mobileir_brands.append(brand)
                mobileir_comments.append(obj['comment'])

mobileir_vectors = vectorizer.transform(mobileir_comments)
mobileir_labels = lsvm.predict(mobileir_vectors)
mobileir_prob = lsvm.predict_proba(mobileir_vectors) 
for i, prob in enumerate(mobileir_prob):
    if (0.4 < mobileir_prob[i][0] < 0.6) or (0.4 < mobileir_prob[i][1] < 0.6):
        mobileir_labels[i] = '2'
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

print("end :)") 