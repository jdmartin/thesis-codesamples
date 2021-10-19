# packages to store and manipulate data
#utility
import os
# package to clean text
import re

# plotting packages
import matplotlib.pyplot as plt
#nltk for data cleaning
import nltk
import numpy as np
import pandas as pd
import seaborn as sns
# model building package
import sklearn
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

files = os.listdir('data')
files.remove('.DS_Store')

for file in files:
    print(file)
    current_file = file.split('.')[0]
    filename = 'data/' + current_file + '.csv'

    df = pd.read_csv(filename)

    def remove_links(text):
        '''Takes a string and removes web links from it'''
        text = re.sub(r'http\S+', '', text) # remove http links
        text = re.sub(r'bit.ly/\S+', '', text) # remove bitly links
        text = text.strip('[link]') # remove [links]
        return text

    def remove_users(text):
        '''Takes a string and removes retweet and @user information'''
        text = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', '', text) # remove retweet
        text = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', text) # remove tweeted at
        return text

    def deEmojify(inputString):
        return inputString.encode('ascii', 'ignore').decode('ascii')

    my_stopwords = nltk.corpus.stopwords.words('english')
    my_es_stopwords = nltk.corpus.stopwords.words('spanish')
    my_custom_stopwords = ['et','w','b','pt','st','I','l']
    word_rooter = nltk.stem.snowball.PorterStemmer(ignore_stopwords=False).stem
    my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@\’”–…'

    # cleaning master function
    def clean_text(text, bigrams=False):
        text = remove_users(text)
        text = remove_links(text)
        text = deEmojify(text)
        text = text.lower() # lower case
        text = re.sub('&amp', '', text) #remove 'amp'
        text = re.sub('['+my_punctuation + ']+', ' ', text) # strip punctuation
        text = re.sub('\s+', ' ', text) #remove double spacing
        text = re.sub('([0-9]+)', '', text) # remove numbers
        text_token_list = [word for word in text.split(' ') if word not in my_custom_stopwords] # remove custom stopwords
        text_token_list = [word for word in text_token_list if word not in my_stopwords] # remove stopwords
        text_token_list = [word for word in text_token_list if word not in my_es_stopwords] # remove spanish stopwords

        #text_token_list = [word_rooter(word) if '#' not in word else word for word in text_token_list] # apply word rooter
        if bigrams:
            text_token_list = text_token_list+[text_token_list[i]+'_'+text_token_list[i+1] for i in range(len(text_token_list)-1)]
        text = ' '.join(text_token_list)
        return text

    df['clean_text'] = df.text.apply(clean_text)

    from sklearn.feature_extraction.text import CountVectorizer

    # the vectorizer object will be used to transform text to vector form
    vectorizer = CountVectorizer(max_df=0.9, min_df=25, token_pattern='\w+|\$[\d\.]+|\S+')

    # apply transformation
    tf = vectorizer.fit_transform(df['clean_text']).toarray()

    # tf_feature_names tells us what word each column in the matrix represents
    tf_feature_names = vectorizer.get_feature_names()

    from sklearn.decomposition import LatentDirichletAllocation

    number_of_topics = 10

    model = LatentDirichletAllocation(n_components=number_of_topics, random_state=0, max_iter=100)

    model.fit(tf)

    def display_topics(model, feature_names, no_top_words):
        topic_dict = {}
        for topic_idx, topic in enumerate(model.components_):
            topic_dict["Topic %d words" % (topic_idx)]= ['{}'.format(feature_names[i]) for i in topic.argsort()[:-no_top_words - 1:-1]]
            topic_dict["Topic %d weights" % (topic_idx)]= ['{:.1f}'.format(topic[i]) for i in topic.argsort()[:-no_top_words - 1:-1]]
        
        #Store topics in file
        with open('topics' + '/' + current_file, 'w') as storage:
            i = 0
            while i < number_of_topics:
                temp_topic = 'topic' + str(i) + '|'
                for item in topic_dict['Topic %d words' % (i)]:
                    temp_topic += (item + ',')
                #Includes Kludge to make trailing comma go away and add new line
                temp_topic = temp_topic[:-1]
                temp_topic += '\n'      

                storage.write(temp_topic)
                i+=1
            storage.close()

        #Store It
        pd.DataFrame(topic_dict).to_csv('output' + '/' + 'topics' + '/' + current_file + '.csv', index = False)

        return pd.DataFrame(topic_dict)

    no_top_words = 10
    print(display_topics(model, tf_feature_names, no_top_words))
