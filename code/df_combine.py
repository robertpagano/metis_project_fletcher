import pandas as pd
import numpy as np
import pickle

##Below functions are for de-duping on df level, stripping live data from each df, merging all non-live with each other, and deduping each merge (so you ned up with one dataframe with ALL non-live statuses)
##If we have dup IDs with different info, will have to figure out what to do
####My thought is that I will order them all by date grabbed, and remove all but the last using drop_duplicates(keep='last')




def unpkl(filename):
	with open(f'/Users/robertpagano/metis_data/project_4/interim/{filename}.pickle', 'rb') as f:
		df = pickle.load(f)
	print('test3')
	return df


def drop_dups(df):
	df.drop_duplicates(subset='id')
	return df


def filter_out_live(df):
	return df.loc[df['state'] != 'live']


def append_df(df_nonlive_master, df):
	'''
	'df_nonlive_master' is master file, 'df' is the new file i'm adding cases from
	it also de-duplicates on id
	'''
	df_nonlive_master = pd.concat([df_nonlive_master, df], ignore_index=True, sort=False)
	df_nonlive_master = df_nonlive_master.drop_duplicates(subset='id')
	return df_nonlive_master


def append_new_live_from_filename(filename, df_nonlive_master):
	df = unpkl(filename)
	df = drop_dups(df)
	df = filter_out_live(df)
	return append_df(df_nonlive_master, df)



## So for non-live master, order is:
## 	1. unpickle df
##	2. drop dups in that df (subset = 'id')
##	3. filter out live
##	4. append to the master
##	5. de-dup master so only adding new closed projects (subset = 'id')
##	6. repeat untill all the way through files


## Then for live master, order is:
##	1. unpickle df
##	2. drop dups in that df (subset = 'id')
##	3. filter out non-live records
##	4. append to master
##	5. sort master by date
##	6. drop dups in master (subset='id', keep='last' so that it keeps the last entry in live (most info))
## 	7. repeat until all the way through files
##	8. Once I have all live records, will need to append all "final statuses" as the final target variable
##			--remove any records that don't have this
##	9. Then I just need to look at my value counts by category, and narrow my focus on category

##	After that, it's NLP time

