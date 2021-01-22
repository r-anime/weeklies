import praw
import configparser
import datetime

c = configparser.ConfigParser()
c.read('config.ini')

reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])
flair_id = c['Options']['flair_weekly_id']

title = datetime.date.today().strftime('Merch Mondays Megathread - Week of %B %d, %Y')
content = """Weekly thread devoted to any and all new merch you may have picked up. If you've got physical goods to show off, it belongs here!

Have a collection you've amassed that you'd like to show off instead? Don't be shy, you can post that here too!

You can also use this thread for questions or advice about buying or collecting anime merch (but remember that selling things is not allowed on /r/anime)."""

post = subreddit.submit(title, selftext=content, flair_id=flair_id)
post.disable_inbox_replies()
post.mod.suggested_sort(sort='new')
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')
