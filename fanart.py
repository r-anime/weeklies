import praw
import configparser
import datetime

c = configparser.ConfigParser()
c.read('config.ini')

reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

title = datetime.date.today().strftime('Weekly Fanart Megathread - Week of %B %d, %Y')
content = """Weekly thread dedicated to all anime fanarts.

Feel free to post your fanart in this thread. The usual restrictions for /r/anime fanart posts do not apply here, so feel free to share anything you want to discuss. Other /r/anime rules still apply, so make sure not to post from illegal sources, heavily NSFW content or untagged spoilers.

Some examples of things you should post here:

- Sketches and other quick drawings that you'd like to share
- WIP fanarts that are not yet ready to be posted
- Fanarts that you did or found and for which you would like advice or feedback
- Any fanart that you can't post because your fanart ratio is too high

Out of respect for other artists and to help with constructive criticism, make sure to properly credit and link the original work if you post a fanart that is not your own or heavily inspired from another work.
"""

post = subreddit.submit(title, selftext=content)
post.disable_inbox_replies()
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')
