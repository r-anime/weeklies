import praw
import configparser
import datetime

c = configparser.ConfigParser()
c.read('config.ini')

reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

title = datetime.date.today().strftime('No Stupid Questions - Week of %B %d, %Y')
content = """Have you ever thought of an anime related question that sounded really, really stupid? Did you ignore it and move on because getting the answer wouldn't be worth asking it? Well, this thread is here for you!

First of all, go take a look at the [/r/anime FAQ section of the wiki](https://www.reddit.com/r/anime/wiki/faaq) since it's entirely possible you might find your question answered there. Failing that, you can take a look at [any of the past threads](https://www.reddit.com/r/anime/search?q=+No+Stupid+Questions+-+Week+of&restrict_sr=on&sort=new&t=all) since someone might've asked the same question there already.

Remember! There are no stupid questions here! Just *slightly less intelligent ones*.

---

Thought of a question a bit too late? No worries! The thread will be at the top of /r/anime throughout the week-end and will get posted again next week!"""

post = subreddit.submit(title, selftext=content)
post.disable_inbox_replies()
post.mod.suggested_sort(sort='new')
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')
