# Bundestag Polls
<img src="/.github/19_viz.png" alt="bundestag19" width="350"/>

I took a machine learning in python course recently and wanted to practice what i have learnt in this course. This repository contains the progress i made in two days with scraping polls from the website of the german [Bundestag](https://bundestag.de).

The poll data was scraped using code in the `scraper` subfolder and stored in csv files in the `data` subfolder.
The files are named as follows: `[Voting Period]_data.csv` containing columns for each poll and are named with the following scheme: `[Period]-[Session]-[Poll]`

Jupyter Notebook `index.ipynb` contains an attempt to do classfication with supervised machine learning using a Pipeling and GridSearchCV. Best Values for 19th Bundestag (Score: 76.78%):
```
{'classifier__knn__n_neighbors': 3, 'classifier__pca__n_components': 4}
```
### Pipeline:
```python
vote_cols = [c for c in df.columns if "-" in c]
Pipeline(steps=[('preprocess',
                 ColumnTransformer(sparse_threshold=0,
                                   transformers=[('preprocess_vote',
                                                  Pipeline(steps=[('imputer',
                                                                   SimpleImputer(fill_value='Abwesend',
                                                                                 strategy='constant')),
                                                                  ('onehot',
                                                                   OneHotEncoder(handle_unknown='ignore'))]),
                                                  vote_cols)])),
                ('classifier',
                 Pipeline(steps=[('pca', PCA()),
                                 ('knn', KNeighborsClassifier())]))])
```

## Result
 The major take-away from this project for me was that you can clearly see in the Visualizations who is the governing coalition in each period and the obligation to vote in accordance with party policy. The classification is not very useful as for yourself to classify a lot of polls have to be taken - although this would be a nice idea for further development.

Visualization is done using tSNE.
### 19th Bundestag:
![](/.github/19_viz.png)
### 18th Bundestag:
![](/.github/18_viz.png)
### 17th Bundestag:
![](/.github/17_viz.png)


### 20th Bundestag (current):
![](/.github/20_viz.png)

### combined Bundestags (does that even make sense? 😉)
![](/.github/all_viz.png)
