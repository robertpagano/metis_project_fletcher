## Kickstart your Kickstarter:

*Intelligent Recommendations for Projects on the Edge*

**Robert Pagano - March 4th, 2019**

## Summary

Kickstarter is a company that hosts a crowdsourcing platform for creators pitching project ideas in the arts, tech, film, games, music, and more. For a given project, a creator will set a fundraising goal, and a target date. If the project meets that fundraising goal through donations of "backers" by the given date, the creator will receive the funds and be held accountable to come through on the project. If they don't meet the goal, none of the pledges are processed and the creator gets nothing.

Some famous successful Kickstarter projects include:

- Exploding Kittens - playing card game from the creator of [The Oatmeal](theoatmeal.com) 
- Cards Against Humanity - playing card game
- OUYA - video game console

The goal of my project is to create a recommendation system that will help promote projects that are on the edge of being successful or not. The project has the following components:

- Random Forest Classifier - utilizing machine learning tools to identify projects that have a 35-70%  chance of becoming successful, given their current progress (how much money they've raised vs. how much time is left), among other features (type of project, time of year, etc.)
- NLP Analysis - utilizing NLP tools and methods to find projects whose descriptions are most similar to each other

As a quick note, below is the kind of text I analyzed - each product's blurb:

![image-20190304131350556](/Users/robertpagano/Library/Application Support/typora-user-images/image-20190304131350556.png)



Through these two processes, the end product will take in a project description and recommend a user similar projects that are within the 35-70% threshold of being successful. This could work in practice by recommending these projects when a user donates to a different project, or otherwise indicates interest in a similar project (through browsing/searching data).

For this project, I also need to point out that I focused only on game projects - I wanted to make sure that at least for my first run through of the whole process, that my NLP analysis wouldn't just recommend all game projects to game projects, music to music, etc. The overall idea is to tune it for one main category, and then iterate through it again to apply it to the entire site (or do one category at a time). For this, though, I was only able to get through one category.

Here is a link to my repo:

https://github.com/robertpagano/metis_project_fletcher



## Tools and Packages Used



| Tools            |
| ---------------- |
| Pandas           |
| NumPy            |
| Matplotlib       |
| Seaborn          |
| Tableau          |
| scikit-learn     |
| Jupyter Notebook |
| Sublime Text     |
| NLTK             |
| Spacy            |
| DBScan           |



## Data Collection and Cleaning



I acquired my data for this project through the below:

https://webrobots.io/kickstarter-datasets/

Web Robots has been scraping Kickstarter project information for the last 5 years, and releasing a new set of data once per month. The data I included in my project was from late 2015 to February 2019.

Data collection and management ended up being a very large part of the process, and took 4-5 days of work.  Each monthly dataset includes around ~50 CSV files and 150-200k unique projects (after deduplicating). So my workflow was the below:

- Data exploration, cleaning, EDA on most recent month (functions found in ks_clean.py):
  - Created function to read all csv files in a directory, and combine them into one, to get all observations for a given month
  - Feature engineering - created features around days project has been live, how much money project has made, etc.
  - Converted any non US projects to USD using adjusted conversion rates (original data only had static, so sometimes converted pledged amount could be under goal, but still counted as success, and vice versa)
  - Converted JSON columns to Pandas columns
    - Ended up being more more difficult than anticipated, had to do quite a bit of 'manual' cleaning as there were issues with nested double quotes. For example, a name value might have a nickname in double quotes, but the entire value would also be in double quotes
- Once I had all my cleaning and formatting functions set, I had to create my script to do this to every months dataset, and merge them together
  - Each month's dataset had over a 90% overlap with the previous month, so when merging, I kept the latest version of each project
  - Created a master "live" data-frame, and a master "final_status" dataframe
    - "Live" dataframe captures a project while it was live at some point
    - "final_status" dataframe captures a project's data when it's final status (success, failed, cancelled) has been resolved
  - Then created my final master dataframe, which takes the "live" dataframe, and appends final status to each project. For any project that has both a "live" status and a "final_status" status, that would be in my final data



I initially did this for all data starting in 2017, but realized I needed additional data, so I went all the way back to 2015.



## Text Analysis - TF IDF and Topic Modeling through LSA and NMF

Once I had fully formatted and cleaned my data, it was time to focus on my text data. As I mentioned previously, I focused only on "games", so I grabbed just those observations, and started my analysis on the "blurbs", the short descriptions listed under every project title on Kickstarter.

I processed the text in a couple steps:

- Utilized Spacy and NLTK for pre-process text, prior to feeding it into the vectorizer
  - NLTK to remove stop-words, special characters, tags, make it lowercase
  - Spacy for lemmatization



![image-20190304125245928](/Users/robertpagano/Library/Application Support/typora-user-images/image-20190304125245928.png)

![image-20190304125304965](/Users/robertpagano/Library/Application Support/typora-user-images/image-20190304125304965.png)



I then ran TfidVecotrizer on the pre-processed data in multiple ways - once with 2 n-grams, and once without n-grams. I then fed each vectorizers into LSA and NMF functions for topic modeling, and created several choices for my topic model final results.

My initial plan here was to use these different versions (LSA with 10, 15, 20, and 25 topics, NMF with the same), and to use them with clustering, and pick which variation worked best in that context. However, I simply ran out of time. I did attempt to cluster this data with both DBscan and K-Means clustering, but ended up scrapping that. I settled on using LSA with 20 topic models as the topics themselves subjectively seemed to make the most sense. Here are a couple of examples:

![img](https://lh5.googleusercontent.com/0LsOpM95gXAfI9SkML5hVTQxZtmywKnmmcJcXKQP2Qw9ov4O8lJ1sRAUiIPxCng5xoY6oTeUuoYJjPSr7Ro2PxBKiEE7TtgmXrFqGVRvODrsH-Ix8i6D7k1UJ3JHp8E7r1GKF9Oz3dA)

![img](https://lh6.googleusercontent.com/MJIj5XSLKvxhvZB7TRVRjXeQKUpk_NRWpmL2EQomOVfNch3Txcn-Ncv5jXjTHJPjWfv4k3bgltYnKc8nUs_KJSCzABLmeodyd3okzXnCgXJBBcBd_p2ZVTHCv686OghfSWbkGPLGW-w)



**Side note about clustering**

I first tried using DBScan. I attempted to manually optimize the hyperparamaters by using the following metrics:

- est. number of clusters
- est. number of noise points
- silhouette coefficient

I did end up getting some seemingly good results there, where I'd get 4-5 clusters with minimal noise points, and a relatively high silhouette coefficient, but then when I plotted it, it seemed to put 99% of all data points into one cluster. So from there, I moved onto K-Means.



With K-means, I was able to get a bit more variance in terms of numbers of projects assigned to different clusters, however, by the time I got to this point, I had only a couple days until the presentation, so I decided to move on to comparing the projects through cosine similarity alone.



**Back to final results**

After selecting my LSA data, I used cosine similarity to determine which blurbs were similar to each other. Through testing various project descriptions, it seemed to be working perfectly, so I was happy with my final tool for finding similar projects through description.

Here is the function itself:



~~~python
def Recommender(Hp, query2, topic_blurb, top_n=10):
    
    cols = ['topic_0', 'topic_1', 'topic_2', 'topic_3',
       'topic_4', 'topic_5', 'topic_6', 'topic_7', 'topic_8', 'topic_9',
       'topic_10', 'topic_11', 'topic_12', 'topic_13', 'topic_14', 'topic_15',
       'topic_16', 'topic_17', 'topic_18', 'topic_19']
    
#     query2 = pre_process2(query2)
    # Transform the query using the same vectorizer as above
    doc_q2 = tfidf5.transform([query2])
    # Use lsa model from above to transform the vectorized query
    doc_topic_q2 = lsa4_20.transform(doc_q2)

    # Create a dataframe of query2
    
    Hp = Hp[cols]
#     print(Hp.shape)
    Qp = pd.DataFrame(doc_topic_q2.round(3),
                    index= [topic_blurb],
                    columns = cols)
#     print(Qp.shape)
    # cosine similarities
    cos_sim = similarEntries(Hp, Qp)

    # Add a new column
    Hp['similarity']= cos_sim
    return Hp, Qp

# make a function that outputs another dataframe with a 'similarity' column added
def similarEntries(Hp, Qp,n=3):
    '''function returns another dataframe
    '''
    nrows = Hp.shape[0]
    Hp = np.asarray(Hp)
    print(Hp.shape)
    Qp = np.asarray(Qp)
    print(Qp.shape)
    
    out = []
    for j in range(nrows):
        out.append(cosine_similarity(Qp.reshape(1,-1), Hp[j,:].reshape(1,-1)))
#         out.append(cosine_similarity(Qp, Hp[j,:]))
    
    cos_sim = out
    
    return [each[0][0] for each in cos_sim]
~~~



Ultimately - this function takes in a dataframe that includes topic models, and filters by just the topic model data ('cols' variable). It also takes in a "query", which is just the actual product blurb that entering to find me the most similar blurb. And finally, just the number of results I want to see, which will be sorted by most similar.

Once I get this dataframe returned with topic similarity appended, I can then use the index to lookup the actual blurbs that it is most similar to:



![image-20190304132127720](/Users/robertpagano/Library/Application Support/typora-user-images/image-20190304132127720.png)



## Classification - Baseline metric, Logistic, and Random Forest modeling 

Now that I have discussed data cleaning and text analysis, I will quickly break down my process for picking my classifier, and getting my final pool of projects that need to be promoted! 

In reality, these steps didn't happen one after another -I actually started my classification work after merging my data frames - but I came back and optimized it once I finalized my text data, so I could potentially use the text data as a part of my feature set.

Before I started optimizing my models, I created a baseline metric - the pace of a project based on the rate of money gained per day, by how many days are left. So more specifically:

money gained per day / money needed to gain per day.

If this was over 1, a project could be said to be "on pace", and if this was below 1, then it had some catching up to do.

I added this statistic as a column in my final data and wanted to see how it compared to whether or not a project eventually ended up succeeding, and here were the results in confusion matrix form:

![image-20190304133150367](/Users/robertpagano/Library/Application Support/typora-user-images/image-20190304133150367.png)



```
Baseline Accuracy: 0.865
Baseline Precision: 0.931
Baseline Recall: 0.763
```



It was doing pretty strongly, so I knew I was going to have to optimize my models quite well to be able to improve on this significantly. The one interesting thing I noticed was that the recall was quite low compared to precision, which means that a significant number of projects were not "on pace" when this data was recorded, but did end up completing. So ultimately, my goal was to be able to have my model figure out when that might occur.

I ended up training 6 different models, and cross validated them all through gridsearchCV:

- Logistic Regression - with all features, including LSA topic models
- Logistic Regression - all features except LSA topic models
- Logistic Regression - only LSA topic model features
- Random Forest Classifier - with all features, including LSA topic models
- Random Forest Classifier  - all features except LSA topic models
- Random Forest Classifier  - only LSA topic model features

My overall best performing model was the random forest classifier, not including the LSA topic models. Here is how it compared to the baseline:

|                       |              |                   |                 |
| --------------------- | ------------ | ----------------- | --------------- |
| **Prediction Metric** | **Baseline** | **RF Classifier** | **Improvement** |
|                       |              |                   |                 |
| **Accuracy**          | 0.865        | 0.947             | 0.082           |
|                       |              |                   |                 |
| **Precision**         | 0.931        | 0.932             | 0.001           |
|                       |              |                   |                 |
| **Recall**            | 0.763        | 0.951             | 0.188           |



Success! It improved fairly significantly overall, and almost 100% of the improvement came in bringing the recall up. This means we were now correctly classifying many more projects that the baseline would expect to fail. This is very important for this problem, because now we can remove more projects from our list of projects to promote, thus giving us more space to promote projects that actually need it!



**Surprisingly**, I actually found that using *only* the LSA topic model data, I was able to predict final success at a 66% accuracy rate with the logistic model. While this outcome was outside the scope of this particular project, I thought it was interesting and could potentially be used to find which types of descriptions help projects succeed vs. others.



## Conclusion

Just to tie everything together, and make sure there is no confusion about what my actual product is, here is the pipeline:

1. Identify which projects on kickstarter need to be promoted using my classification model. This will create a pool of projects that are within some threshold of being successful (for my project, I chose 35-70%). This allows us to *not* promote projects that should likely be successful, so we can focus on those that need a bit more of a boost
2. When a user either donates to a project, or otherwise shows interest in a project, use the cosine similarity tool to recommend projects that are most similar from the previously mentioned pool of projects



## Future Work



There are quite a few potential options for future work with this project:

**Clustering on text data** / **optimizing LSA **- rather than using cosine similarity to identify similar projects, it would be computationally more efficient to simply recommend projects that are within a certain cluster. This seems very doable, however, I simply didn't have time to explore this option completely.

I could also use the clustering process to optimize how many topics I should use in my LSA or NMF transformations.

**Looking at all categories** - ultimately, it would be great if this tool could be used to promote projects *outside* of a given main category. So for example, if a user is interested in fantasy games, maybe they'd be interested in fantasy art, as well

**Fraud Detection** - through my classifier, I could see that some projects that had a very low chance of succeeding, did in fact succeed:

![img](https://lh6.googleusercontent.com/Hz6n5b6-Z8oy8gvYC70JqTwYHAyuNKBe_kT1zWVSfAAtrTsILJ_tv-OxOri3lLlAUJYJu6d7XFUIDKyInC-zCrhu1pvVJl0Wn7lw4bKYlbHXx5PlQeiCn7ijVfSahjePr6kGVTjKZ-g)

There is a bit of a reputation for Kickstarter that many creators will simply dump in whatever remaining pledges are needed at the last minute, so they can pocket the real pledges when the deadline hits. You could use this classifier to flag projects to investigate further, to see if this is actually happening.

**Make recommender tool user friendly** - could create a Flask App to show how this works conceptually. Right now, it's a lot of manual code