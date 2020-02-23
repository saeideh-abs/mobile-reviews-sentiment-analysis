"""
first accuracy: 0.64 (if svm_prob <= 0.9 then used lexicon labels if it was in [-3, 5])
second accuracy: hybrid approach accuracy: 0.8293577981651377
                 svm accuracy:             0.8165137614678899
                 lexicon based accuracy:   0.7027522935779816
                 (if svm_prob <= 0.8 then used lexicon labels if it was in [-2, 5])
"""
import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection  import GridSearchCV
from sklearn import svm
from nltk.metrics.scores import (accuracy)
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score 
import items_ranking
import correlation

#lexicon based approach
def sentence_polarity(comment):
  score = 0
  words = comment.split()
  for index, word in enumerate(words):
      if word in positive_words:
          score += 1
      if word in negative_words:
          score += -1
      if word in negative_verbs:
          for i in range(2): #setting range to 2 gives best accuracy
              if index-i >= 0 :
                  if words[index-i] in positive_words:
                      score += -2
                  if words[index-i] in negative_words:
                      score += 2
  if score >= 1:
      label = '1'
  elif score == 0:
      label = '2'
  else:
      label = '0'
  return score, label

def svm_lexicon_hybrid(svm_labels, svm_probs, lexicon_labels, lexicon_scores):
    hybrid_labels = []
    for i in range(len(svm_labels)):
        if svm_labels[i] == lexicon_labels[i]:
            #print("equal")
            hybrid_labels.append(svm_labels[i])
        elif svm_probs[i][0] >= 0.8 or svm_probs[i][1] >= 0.8:
            #print("svm was >= 0.8")
            hybrid_labels.append(svm_labels[i])
        elif ((svm_probs[i][0] >= 0.5 or svm_probs[i][1] >= 0.5) and
             (lexicon_scores[i] <= -2 or lexicon_scores[i] >= 5)):
            #print("svm was >= 0.5 and lexicon >= 5 or -2")
            hybrid_labels.append(lexicon_labels[i])
        else:
            #print("svm was >= 0.5 and lexicon in [-2, 5]")
            hybrid_labels.append(svm_labels[i])
            
    return hybrid_labels
    

################################## variables ##################################
train_comments = []
test_comments = []
train_labels = []
test_labels = []
lexicon_labels = []
lexicon_scores = []
mobileir_brands = []
mobileir_comments = []
mobileir_lexicon_labels = []
mobileir_lexicon_scores = []
popular_brands_names = []
################################# reading data ################################
with open('../dataset/mobile.ir.final.json', encoding="utf8") as json_file:
    mobile_ir = json.load(json_file)
mobile_brands = open("../dataset/mobile_brands.txt", encoding="utf8").read().split('\n')

dataset = open("../dataset/mobile_digikala.csv", encoding="utf8").read().split('\n') #read dataset
dataset = dataset[1:] #remove csv headers
train_data, test_data = train_test_split(dataset, test_size = 0.2)
train_len = len(train_data) #2453
test_len = len(test_data) #273

positive_words = open("../dataset/dataheart_lexicon/positive_words.txt", encoding="utf8").read().split('\n') 
negative_words = open("../dataset/dataheart_lexicon/negative_words.txt", encoding="utf8").read().split('\n') 
negative_verbs = open("../dataset/dataheart_lexicon/negative_verbs.txt", encoding="utf8").read().split('\n') 

digikala_ranking = open("../dataset/digikala_ranking.txt", encoding="utf8").read().split('\n')
cafebazar_ranking = open("../dataset/cafebazar_ranking.txt", encoding="utf8").read().split('\n')
gs_statcounter_ranking = open("../dataset/gs.statcounter_ranking.txt", encoding="utf8").read().split('\n')

################################# preproccessing ##############################
for comment in train_data:
    comment = comment.split(',')
    train_comments.append(comment[1])
    train_labels.append(comment[0])
for comment in test_data:
    comment = comment.split(',')
    test_comments.append(comment[1])
    test_labels.append(comment[0])
    #detect labels using lexicon
    score, sent_polarity = sentence_polarity(comment[1])
    lexicon_labels.append(sent_polarity)
    lexicon_scores.append(score)
    
################################ svm training #################################
print("************************ svm training ********************************")
vectorizer = TfidfVectorizer(min_df = 5, max_df = 0.8, sublinear_tf = True, use_idf = True)

train_vectors = vectorizer.fit_transform(train_comments)
test_vectors = vectorizer.transform(test_comments)

param_grid = {'C': [0.01, 0.1, 1, 10, 100], 'kernel': ['rbf', 'linear']}
svm = GridSearchCV(svm.SVC(class_weight='balanced', probability=True), param_grid)
svm.fit(train_vectors, train_labels)
svm_labels = svm.predict(test_vectors)
svm_prob= svm.predict_proba(test_vectors)

############################### hybrid approach ###############################
print("*********************** hybrid approch phase *************************")
hybrid_labels = svm_lexicon_hybrid(svm_labels, svm_prob, lexicon_labels, lexicon_scores)

############################### Evaluation ####################################
print("************************** accuracy **********************************")
hybrid_accuracy = accuracy(test_labels, hybrid_labels)
print("hybrid approach accuracy:", hybrid_accuracy)
svm_accuracy = accuracy(test_labels, svm_labels)
print("svm accuracy:", svm_accuracy)
lexicon_accuracy = accuracy(test_labels, lexicon_labels)
print("lexicon based approach accuracy:", lexicon_accuracy)

precision = precision_score(test_labels, hybrid_labels, labels=None, average='weighted')
print("hybrid precision:", precision)
recall = recall_score(test_labels, hybrid_labels, labels=None, average='weighted')
print("hybrid recall:", recall)


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
                score, sent_polarity = sentence_polarity(obj['comment'])
                mobileir_lexicon_labels.append(sent_polarity)
                mobileir_lexicon_scores.append(score)
    

mobileir_vectors = vectorizer.transform(mobileir_comments)
mobileir_svm_labels = svm.predict(mobileir_vectors)
mobileir_svm_prob = svm.predict_proba(mobileir_vectors) 
for i, prob in enumerate(mobileir_svm_prob):
    if (0.4 < mobileir_svm_prob[i][0] < 0.6) or (0.4 < mobileir_svm_prob[i][1] < 0.6):
        mobileir_svm_labels[i] = '2'

mobileir_hybrid_labels = svm_lexicon_hybrid(mobileir_svm_labels, mobileir_svm_prob, mobileir_lexicon_labels, mobileir_lexicon_scores)

brands_ranking = items_ranking.ranking(mobileir_brands, mobileir_hybrid_labels)   
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