import praw
import configparser
import datetime

c = configparser.ConfigParser()
c.read('config.ini')

reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

title = datetime.date.today().strftime('Miscellaneous Anime Questions - Week of %B %d, %Y')
content = """Have any random questions about anime that you want answered, but don't think deserve their own dedicated thread? Or maybe because you think it might just be silly? Then this is the thread for you!

Also [check our FAQ](https://www.reddit.com/r/anime/wiki/faaq).

Remember! There are miscellaneous questions here!

---

Thought of a question a bit too late? No worries! The thread will be at the top of /r/anime throughout the week-end and will get posted again next week!"""

post = subreddit.submit(title, selftext=content)
post.disable_inbox_replies()
post.mod.suggested_sort(sort='new')
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')
