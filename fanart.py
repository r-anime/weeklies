import praw
import configparser
import datetime

c = configparser.ConfigParser()
c.read('config.ini')

reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

title = datetime.date.today().strftime('Fanart Wednesday Megathread - Week of %B %d, %Y')
content = """Weekly thread dedicated to fanarts from our community.

Feel free to post your fanart in this thread. The usual restrictions for /r/anime fanart posts do not apply here, so feel free to share anything you've drawn.

In particular, you should use this thread to post the following:

- Sketches and other quick drawings that you'd like to share
- WIP fanarts that are not yet ready to be posted
- Fanarts for which you would like advice or feedback
- Any fanart that you can't post because your fanart ratio is too high
- Heavily referenced works that don't count as OC

Out of respect for other artists and to help with constructive criticism, make sure to properly credit and link the original work if you post a fanart that is not your own or heavily inspired from another work.
"""

post = subreddit.submit(title, selftext=content)
post.disable_inbox_replies()
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')
