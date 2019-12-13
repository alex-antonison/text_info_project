import pandas as pd
import numpy as np
import os

from os import path
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')

def plot_10_most_common_words(count_data, count_vectorizer):
    import matplotlib.pyplot as plt
    words = count_vectorizer.get_feature_names()
    total_counts = np.zeros(len(words))
    for t in count_data:
        total_counts+=t.toarray()[0]
    count_dict = (zip(words, total_counts))
    count_dict = sorted(count_dict, key=lambda x:x[1], reverse=True)[0:10]
    words = [w[0] for w in count_dict]
    counts = [w[1] for w in count_dict]
    x_pos = np.arange(len(words))

    plt.figure(2, figsize=(15, 15/1.6180))
    plt.subplot(title='10 most common words')
    sns.set_context("notebook", font_scale=1.25, rc={"lines.linewidth": 2.5})
    sns.barplot(x_pos, counts, palette='husl')
    plt.xticks(x_pos, words, rotation=90)
    plt.xlabel('words')
    plt.ylabel('counts')
    plt.show()

def plot_Graph(long_string):

    # Generate a word cloud image

    # Display the generated image:
    # the matplotlib way:
    import matplotlib.pyplot as plt

    # lower max_font_size
    wordcloud = WordCloud(max_font_size=40).generate(long_string)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

def calculate_LDA(count_data,count_vectorizer,number_topics,number_words,col_name):
    import warnings
    warnings.simplefilter("ignore", DeprecationWarning)

    # Load the LDA model from sk-learn
    from sklearn.decomposition import LatentDirichletAllocation as LDA
           

    # Create and fit the LDA model
    lda = LDA(n_components=number_topics)
    lda.fit(count_data)

    # Print the topics found by the LDA model
    print("Topics found via LDA for ",col_name)
    print_topics(lda, count_vectorizer, number_words)

# Helper function
def print_topics(model, count_vectorizer, n_top_words):
    words = count_vectorizer.get_feature_names()
    for topic_idx, topic in enumerate(model.components_):
        print("\nTopic #%d:" % topic_idx)
        print(" ".join([words[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))


def doing_data_analysis(bag_of_words,col_name,number_topics,number_words):

    #Initialise the count vectorizer with the English stop words
    count_vectorizer = CountVectorizer(stop_words='english')

    """
        These are the steps are happening in the following lines :
            1. Getting each column for processing
            2. Adding those and creating a word cloud to check the max occurance
            3. Showing a graph and plaotting it based on the 10 most common use words
            4. Performing LDA based on the column with number of words and number of topic

    """

    long_string = ','.join(list(bag_of_words.values))
    plot_Graph(long_string)
    #Fit and transform the processed titles
    count_data = count_vectorizer.fit_transform(bag_of_words)
    #Visualise the 10 most common words
    plot_10_most_common_words(count_data, count_vectorizer)
    #calculating LDA for preliminary-report
    calculate_LDA(count_data,count_vectorizer,number_topics,number_words,col_name)



def main():
    candidate_col = pd.read_csv('final_Report.csv')
 #   candidate_col = candidate_col.drop(columns=[
 #   'report-url', 'accidnet-classification', 'location', 'mine-type', 'mine-controller', 'mined-mineral', 'incident-date', 'public-notice','fatality-alert','final-report'], axis=1)
    # Print out the first rows of candidate_col
    candidate_col.head()

    """
        These are the steps are happening in the following lines :
            1. Getting each column for processing
            2. Adding those and creating a word cloud to check the max occurance
            3. Showing a graph and plaotting it based on the 10 most common use words
            4. Performing LDA based on the column with number of words and number of topic

   
    #   doing_data_analysis  
        Arguments:
            col_values      : The data associated in that column
            col_name        : The column name
            number_topics   : How many topic will be the outcome
            number_words    : How many words will be in each topic
    """

    #   doing text analysis for the location
    doing_data_analysis(candidate_col['location'],'location',5,1)

    #   doing text analysis for the preliminary-report
    doing_data_analysis(candidate_col['preliminary-report'],'report',5,10)

     #   doing text analysis for the mine-type
    doing_data_analysis(candidate_col['mine-type'],'mine-type',5,1)

     #   doing text analysis for the mine-controller
    doing_data_analysis(candidate_col['mine-controller'],'mine-controller',5,10)

     #   doing text analysis for the accidnet-classification
    doing_data_analysis(candidate_col['accidnet-classification'],'accidnet-classification',5,10)

     #   doing text analysis for the fatality-alert
    doing_data_analysis(candidate_col['fatality-alert'],'fatality-alert',5,50)

     #   doing LDA on Final report
    count_vectorizer_1 = CountVectorizer(stop_words='english')
    count_data_1 = count_vectorizer_1.fit_transform(candidate_col['final-report'])
    calculate_LDA(count_data_1,count_vectorizer_1,5,75,'final-report')


if __name__ == '__main__':
    main()
