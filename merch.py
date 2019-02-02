import praw
import configparser
import datetime

c = configparser.ConfigParser()
c.read('config.ini')

reddit = praw.Reddit(**c['Auth'])

title = datetime.date.today().strftime('Merch Mondays Megathread - Week of %B %d, %Y')
content = """Weekly thread devoted to any and all new merch you may have picked up. If you've got physical goods to show off, it belongs here!

Have a collection you've amassed that you'd like to show off instead? Don't be shy, you can post that here too!"""

subreddit = reddit.subreddit('anime')
post = subreddit.submit(title, selftext=content)
post.disable_inbox_replies()
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')
