import pandas as pd
import numpy as np
import glob, os
import datetime
import json

'''
These functions should fully clean all raw csv files from https://webrobots.io/kickstarter-datasets/
The biggest issue is that several important features are grouped together in columns that have unprocessed JSON data that requires some cleaning to turn into Pandas columns
'''


def build_dataframe(path):
	'''
	this merges all files for each datapull into one dataframe
	'''
	all_files = glob.glob(os.path.join(path, "*.csv"))
	list_ = []
	for file_ in all_files:
		df = pd.read_csv(file_,index_col=None, header=0)
		list_.append(df)
	return pd.concat((pd.read_csv(f) for f in all_files)).reset_index()


def add_current_date(df, path):
	'''
	This pulls the date from the end of the folder name to create a "current date" column. Denotes the date the data was scraped
	'''
	current_date = pd.to_datetime(path[-10:])
	df['current_date'] = current_date
	return df


def create_date_cols(df):
	'''
	creates custom datetime columns, and time_to_launch, day_limit
	'''
	df['date_created'] = pd.to_datetime(df['created_at'], unit='s') # when project creator started work on project
	df['deadline_date'] = pd.to_datetime(df['deadline'], unit='s')
	df['launched_date'] = pd.to_datetime(df['launched_at'], unit='s') # when creator launched project, starts countdown for deadline
	df['date_state_changed'] = pd.to_datetime(df['state_changed_at'], unit='s') # when creator launched project, starts countdown for deadline
	df['time_to_launch'] = (df['launched_date'] - df['date_created']).dt.days # num days from creation to launch
	df['day_limit'] = (df['deadline_date'] - df['launched_date']).dt.days # num days from launch to deadline
	return df


def creat_date_cols_2(df):
	'''
	additional date calculation columns:
		- days remain after close (how early a projct closed) ##removed this because projects stay live even if they make it
		- days left (how much time a "live project" has, ignore for closed projects)
	'''
	# df['days_remain_after_close'] = (df['deadline_date'] - df['date_state_changed']).dt.days
	df['days_left'] = (df['deadline_date'] - df['current_date']).dt.days
	df['days_in_field'] = (df['current_date'] - df['launched_date']).dt.days + 1
	return df

def clean_days_in_field(df):
	'''
	adds 1 day to those projects that started on same day as data pull
	'''
	df['days_in_field'] = df['days_in_field'].where((df['days_in_field'] != 0), 1)
	return df

def calc_manual_conversion_rate(df):
	'''
	creates a manual conversion rate. converted_pledged_amount comes straight from kickstarter, whereas "fixed_rate" column came from scraper. This way I am using the same calculation on goal that kickstarter originally did
	'''
	df['manual_usd_rate'] = df['converted_pledged_amount'] / (df['pledged'].astype(int))
	return df


def convert_goal_manually(df):
	'''
	converts goal to USD value
	if my manual rate is non-finite (due to pledged being '0'), go with the static rate provided
	'''
	try:
		df['converted_goal'] = df['goal'] * df['manual_usd_rate']
		df['converted_goal'] = df['converted_goal'].round(0).astype(int)
	except ValueError:
		df['converted_goal'] = df['goal'] * df['static_usd_rate']
		df['converted_goal'] = df['converted_goal'].round(0).astype(int)
	return df


def clean_creator(text):
	'''
	cleans the text within creator column. used in function 'clean_creator_col' to clean the entire column
	'''
	head, sep, tail = text.partition(',"name"')
	return head + '}'


def clean_creator_col(df):
	'''
	creates column that can then be processed with json.loads
	'''
	df['creator_cleaned'] = df['creator'].apply(clean_creator)
	return df


def clean_url(text):
	'''
	cleans the text within url column. used in function 'clean_url_col' to clean the entire column
	'''
	head, sep, tail = text.partition('"web":')
	text = tail
	return tail[:-1]
	

def clean_url_col(df):
	'''
	creates column that can then be processed with json.loads
	'''
	df['urls_cleaned'] = df['urls'].apply(clean_url)
	return df


def clean_profile(text):
	'''
	cleans the text within profile column. used in function 'clean_profile_col' to clean the entire column
	'''
	head, sep, tail = text.partition(',"state":')
	return head + '}'


def clean_profile_col(df):
	'''
	creates column that can then be processed with json.loads
	'''
	df['profile_cleaned'] = df['profile'].apply(clean_profile)
	return df


# def clean_location(text):
#     '''
#     cleans the text within location column. used in function 'clean_location_col' to clean the entire column
#     '''
#     head, sep, tail = text.partition(',"slug":')
#     return head + '}'


#  def clean_location_col(df):
#     '''
#     creates column that can then be processed with json.loads
#     '''
#     df['location_cleaned'] = df['location'].apply(clean_location)
#     return df


def convert_json_columns(df):
	'''
	converts columns with json data to separate columns, using original column name as prefix
	### NOTE must be used after the previous cleaning functions
	### NOTE that location column is still throwing errors - ignoring for now as probably don't need geographic data for analysis
	'''
	
	#category column **WORKING - doesn't need preprocessing**
	cat_df = df['category'].apply(json.loads)
	cat_df = pd.DataFrame(cat_df.tolist()).add_prefix('category_')
	df = pd.merge(df, cat_df, left_index=True, right_index=True, how='outer')
	
	#creator column **WORKING**
	creator_df = df['creator_cleaned'].apply(json.loads)
	creator_df = pd.DataFrame(creator_df.tolist()).add_prefix('creator_')
	df = pd.merge(df, creator_df, left_index=True, right_index=True, how='outer')
	
#     #location column **NOT WORKING - I think it's due to null values, but this data isn't important**
#     location_df = df['location_cleaned'].apply(json.loads)
#     location_df = pd.DataFrame(location_df.tolist()).add_prefix('location_')
#     df = pd.merge(df, location_df, left_index=True, right_index=True, how='outer')
	
	#profile column **WORKING**
	profile_df = df['profile_cleaned'].apply(json.loads)
	profile_df = pd.DataFrame(profile_df.tolist()).add_prefix('profile_')
	df = pd.merge(df, profile_df, left_index=True, right_index=True, how='outer')
	
	#urls column **WORKING (but need to clean a bit first like with creator)**
	urls_df = df['urls_cleaned'].apply(json.loads)
	urls_df = pd.DataFrame(urls_df.tolist()).add_prefix('urls_')
	df = pd.merge(df, urls_df, left_index=True, right_index=True, how='outer')
	
	return df


def clean_final_1(path):
	df = build_dataframe(path)
	create_date_cols(df)
	add_current_date(df, path)
	creat_date_cols_2(df)
	clean_days_in_field(df)
	calc_manual_conversion_rate(df)
	convert_goal_manually(df)
	clean_creator_col(df)
	clean_url_col(df)
	clean_profile_col(df)
	return convert_json_columns(df)


####PART 2

def clean_cat_slug(text):
	'''
	cleans the text within cat_slug column. used in function 'separate_main_cat' to create main cat column
	'''
	head, sep, tail = text.partition('/')
	return head


def separate_main_cat(df):
	df['category_main'] = df['category_slug'].apply(clean_cat_slug)
	return df


def update_state(df):
	'''
	changes state to "success" if pledged amount greater than goal/ Mainly updates "live" projects to success, and some cancelled ones, which is OK
	'''
	df['state'] = df['state'].where((df['converted_pledged_amount'] < df['converted_goal']), 'successful')
	return df


def calc_money_left(df):
	'''
	calculates how short of goal projects are. ignore unless live
	'''
	df['remaining_money_needed'] = df['converted_goal'] - df['converted_pledged_amount']
	return df

def calc_money_left_per_day(df):
	'''
	calculates how much money need each day to achieve success
	'''
	df['money_needed_by_day'] = df['remaining_money_needed'] / df['days_left']
	return df

def calc_money_gained_per_day(df):
	'''
	calculates how much money project has gained per day on average
	'''
	df['money_gained_per_day'] = df['converted_pledged_amount'] / df['days_in_field']
	return df

def divide_current_rate_by_remaining_rate(df):
	'''
	calculates how close the current rate and remaining rate are. The closer this is to 0, the worse the project is doing
	'''
	df['current_by_remaining_rate'] = df['money_gained_per_day'] / df['money_needed_by_day']
	return df

def drop_columns(df):
	'''
	removing "static_usd_rate" from this list because I will need it to convert non-USD goals
	'''
	return df.drop(columns=['index', 'category', 'created_at', 'creator', 'currency', 'currency_symbol', 'currency_trailing_code', 'current_currency', 'deadline', 'disable_communication', 'friends', 'fx_rate', 'is_backing', 'is_starrable', 'is_starred', 'launched_at', 'location', 'permissions', 'photo', 'profile', 'source_url', 'spotlight', 'urls', 'usd_type', 'creator_cleaned', 'urls_cleaned', 'profile_cleaned', 'category_color', 'category_parent_id', 'category_urls', 'urls_message_creator', 'urls_rewards'])


def clean_final_2(df):
	separate_main_cat(df)
	update_state(df)
	calc_money_left(df)
	calc_money_left_per_day(df)
	calc_money_gained_per_day(df)
	divide_current_rate_by_remaining_rate(df)
	return drop_columns(df)


##Test to see if all can be done in one function
##For some reason, it throws an error at "separate_main_cat"
##For now, it works just fine to do 1 and then 2

# def clean_final_3(path):
# 	df = build_dataframe(path)
# 	create_date_cols(df)
# 	clean_creator_col(df)
# 	clean_url_col(df)
# 	clean_profile_col(df)
# 	convert_json_columns(df)
# 	separate_main_cat(df)
# 	return drop_columns(df)


##Current date addition, need to add manually in between steps 1 and 2:


