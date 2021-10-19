# packages to store and manipulate data
import os
# utils
import re

files = os.listdir('data/flattened')
#Remove unwanted files:
files.remove('.DS_Store')
files.remove('DHSI20_flat.csv')

# plotting packages
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
# model building package
import sklearn

for file in files:
    print(file)
    current_file = file.split('.')[0]
    filename = 'data/flattened/' + current_file + '.csv'

    df = pd.read_csv(filename)
    df.text.unique().shape

    # make a new column to highlight retweets
    df['is_retweet'] = df['text'].apply(lambda x: x[:2]=='RT')
    df['is_retweet'].sum()  # number of retweets

    # number of unique retweets
    df.loc[df['is_retweet']].text.unique().size

    # 10 most repeated tweets
    highRT = df.groupby(['text']).size().reset_index(name='counts').sort_values('counts', ascending=False).head(10)

    #Store It
    pd.DataFrame(highRT).to_csv('output' + '/' + 'highRT' + '/' + current_file + '.csv', index = False)

    # number of times each tweet appears
    counts = df.groupby(['text']).size().reset_index(name='counts').counts

    # define bins for histogram
    my_bins = np.arange(0,counts.max()+2, 1)-0.5

    def find_retweeted(text):
        '''This function will extract the twitter handles of retweeted people'''
        return re.findall('(?<=RT\s)(@[A-Za-z]+[A-Za-z0-9-_]+)', text)

    def find_mentioned(text):
        '''This function will extract the twitter handles of people mentioned in the tweet'''
        return re.findall('(?<!RT\s)(@[A-Za-z]+[A-Za-z0-9-_]+)', text)

    def find_hashtags(text):
        '''This function will extract hashtags'''
        return re.findall('(#[A-Za-z]+[A-Za-z0-9-_]+)', text)

    # make new columns for retweeted usernames, mentioned usernames and hashtags
    df['retweeted'] = df.text.apply(find_retweeted)
    df['mentioned'] = df.text.apply(find_mentioned)
    df['hashtags'] = df.text.apply(find_hashtags)

    # take the rows from the hashtag columns where there are actually hashtags
    hashtags_list_df = df.loc[df.hashtags.apply(lambda hashtags_list: hashtags_list !=[]),['hashtags']]

    # create dataframe where each use of hashtag gets its own row
    flattened_hashtags_df = pd.DataFrame([hashtag for hashtags_list in hashtags_list_df.hashtags for hashtag in hashtags_list], columns=['hashtag'])

    # number of unique hashtags
    print('Number of Unique Hashtags: ' + str(flattened_hashtags_df['hashtag'].unique().size))

    # count of appearances of each hashtag
    print('Appearances of Each Hashtag')
    print(flattened_hashtags_df.groupby('hashtag').size().reset_index(name='counts').sort_values('counts', ascending=False).reset_index(drop=True))
    popular_hashtags = flattened_hashtags_df.groupby('hashtag').size().reset_index(name='counts').sort_values('counts', ascending=False).reset_index(drop=True)
    #Store It
    pd.DataFrame(popular_hashtags).to_csv('output' + '/' + 'hashtags' + '/' + current_file + '.csv', index = False)

    ###Visualizing
    # take hashtags which appear at least this amount of times
    min_appearance = 25

    # find popular hashtags - make into python set for efficiency
    popular_hashtags_set = set(popular_hashtags[popular_hashtags.counts>=min_appearance]['hashtag'])

    # make a new column with only the popular hashtags
    hashtags_list_df['popular_hashtags'] = hashtags_list_df.hashtags.apply(lambda hashtag_list: [hashtag for hashtag in hashtag_list if hashtag in popular_hashtags_set])

    # drop rows without popular hashtag
    popular_hashtags_list_df = hashtags_list_df.loc[hashtags_list_df.popular_hashtags.apply(lambda hashtag_list: hashtag_list !=[])]

    # make new dataframe
    hashtag_vector_df = popular_hashtags_list_df.loc[:, ['popular_hashtags']]

    #Just the first 18
    i = 0
    for hashtag in popular_hashtags_set:
        if i <= 17:
        # make columns to encode presence of hashtags
            hashtag_vector_df['{}'.format(hashtag)] = hashtag_vector_df.popular_hashtags.apply(lambda hashtag_list: int(hashtag in hashtag_list))
            i+=1

    hashtag_matrix = hashtag_vector_df.drop('popular_hashtags', axis=1)

    # calculate the correlation matrix
    correlations = hashtag_matrix.corr()

    # # plot the correlation matrix
    plt.figure(figsize=(25, 25))
    ax=plt.subplot(111)
    sns.set(font_scale=1.5) # font size 2
    sns.color_palette("icefire", as_cmap=True)
    sns.heatmap(correlations, annot=True, fmt=".1g", center=0, linecolor='white', linewidths=.5, robust=True, vmin=-1, vmax=1, cbar_kws={'label':'correlation'}, ax=ax)
    
    ax.tick_params(labelsize='19', width=3)
    ax.tick_params(axis='x', which='minor', labelsize=9, width=3)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    
    plt.savefig('output' + '/' + 'plots' + '/' + current_file + '.png')
