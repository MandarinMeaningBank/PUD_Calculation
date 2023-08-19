import numpy as np # to handle numeric data
import seaborn as sns
import matplotlib.pyplot as plt # for visualization
import pandas as pd # for handling dataframe
import scipy.cluster.hierarchy as sch # importing scipy.cluster.hierarchy for dendrogram
from scipy.spatial.distance import pdist
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
import tikzplotlib

ourData = pd.read_csv('PUD-2.csv') # read the data
print(ourData.shape)# print the first five rows of our dataset
print(ourData.columns)

ourData = ourData.drop('languageID', axis=1)
print(ourData.head)

scaler = StandardScaler()
ourDataStd = scaler.fit_transform(ourData)
# print(ourDataStd)


METHOD = "ward"
linkage = sch.linkage(ourDataStd, method = METHOD, metric="euclidean") # finding the optimal number of clusters using dendrogram

dendrogram = sch.dendrogram(linkage)
# plt.axhline(y = 45, color = 'r', linestyle = '-')
plt.title('Dendrogram') # title of the dendrogram
plt.xlabel('languages') # label of the x-axis
plt.ylabel('Euclidean distances') # label of the y-axis
plt.show() # show the dendrogram
# tikzplotlib.save('filename.tex')














