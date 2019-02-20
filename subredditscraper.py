# Code from https://towardsdatascience.com/scraping-reddit-with-praw-76efc1d1e1d9

class SubredditScraper:

    def __init__(self, sub, sort='new', lim=900, mode='w'):
        self.sub = sub
        self.sort = sort
        self.lim = lim
        self.mode = mode
        print(
            f'SubredditScraper instance created with values '
            f'sub = {sub}, sort = {sort}, lim = {lim}, mode = {mode}')

    # Next, we’ll set the sorting method for our subreddit instance.
	#This method will set the subreddit and sorting parameters of the Reddit instance to the values we specify when instantiating our class. This will return a tuple that we’ll unpack in the next method. If the sorting method is not new, top, or hot it will default to hot.
	def set_sort(self):
		if self.sort == 'new':
			return self.sort, reddit.subreddit(self.sub).new(limit=self.lim)
		elif self.sort == 'top':
			return self.sort, reddit.subreddit(self.sub).top(limit=self.lim)
		elif self.sort == 'hot':
			return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
		else:
			self.sort = 'hot'
			print('Sort method was not recognized, defaulting to hot.')
			return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)

	#Finally, we can begin collecting posts and other information from the specified subreddit:

	def get_posts(self):
    """Get unique posts from a specified subreddit."""

    	sub_dict = {
        	'selftext': [], 'title': [], 'id': [], 'sorted_by': [],
        	'num_comments': [], 'score': [], 'ups': [], 'downs': []}
    	csv = f'{self.sub}_posts.csv'

    	# Attempt to specify a sorting method.
    	sort, subreddit = self.set_sort()

    	# Set csv_loaded to True if csv exists since you can't 
    	# evaluate the truth value of a DataFrame.
    	df, csv_loaded = (pd.read_csv(csv), 1) if isfile(csv) else ('', 0)

    	print(f'csv = {csv}')
    	print(f'After set_sort(), sort = {sort} and sub = {self.sub}')
    	print(f'csv_loaded = {csv_loaded}')

    	print(f'Collecting information from r/{self.sub}.')


    	for post in subreddit:

    # Check if post.id is in df and set to True if df is empty.
    # This way new posts are still added to dictionary when df = ''
    	unique_id = post.id not in tuple(df.id) if csv_loaded else True

    # Save any unique posts to sub_dict.
    	if unique_id:
       		sub_dict['selftext'].append(post.selftext)
        	sub_dict['title'].append(post.title)
        	sub_dict['id'].append(post.id)
        	sub_dict['sorted_by'].append(sort)
        	sub_dict['num_comments'].append(post.num_comments)
        	sub_dict['score'].append(post.score)
        	sub_dict['ups'].append(post.ups)
        	sub_dict['downs'].append(post.downs)
    	sleep(0.1)