# packages to store and manipulate data
import pandas as pd
import numpy as np
import os

from os import path
from wordcloud import WordCloud


papers = pd.read_csv('final_Report.csv')

papers = papers.drop(columns=[
'report-url', 'accidnet-classification', 'location', 'mine-type', 'mine-controller', 'mined-mineral', 'incident-date', 'public-notice','preliminary-report','fatality-alert'], axis=1)
# Print out the first rows of papers
papers.head()


long_string = ','.join(list(papers['final-report'].values))

#xa0
#print(long_string)
# Create a WordCloud object
#wordcloud = WordCloud(background_color="white", max_words=5000, contour_width=3, contour_color='steelblue')
# Generate a word cloud
#wordcloud.generate(long_string)
# Visualize the word cloud
#wordcloud.to_image()


# Generate a word cloud image
wordcloud = WordCloud().generate(long_string)

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

# lower max_font_size
wordcloud = WordCloud(max_font_size=40).generate(long_string)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

