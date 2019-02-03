import praw
import configparser
import datetime

c = configparser.ConfigParser()
c.read('config.ini')

reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

title = datetime.date.today().strftime('Recommendation Tuesdays Megathread - Week of %B %d, %Y')
content = """
Need a recommendation or have one to share? This is your thread! This thread is active all week, so you can post in it when it's not Tuesday and still get an answer! :)

If you have a recommendation to share that's well written and longer than 1.5k characters, consider instead posting a [WT!] (Watch This!) thread.

If you'd like to look through the previous WT! threads to find recommendations or check if there is already one for your favourite show, [click here.](https://docs.google.com/spreadsheets/d/13JtLBsaUlkIYgokKV0CQo0naTL7TuVcTELturmAVRxo/edit#gid=0)

**Not sure how to ask for a recommendation?** Fill this out, or simply use it as a guideline, and other users will find it much easier to recommend you an anime!

*I'm looking for:* A certain genre? Something specific like characters travelling to another world? etc

*Shows I've already seen that are similar:*

*Link to my MAL (or other anime list):* Leave blank if you don't have one.
"""

post = subreddit.submit(title, selftext=content)
post.disable_inbox_replies()
post.mod.suggested_sort(sort='new')
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')
