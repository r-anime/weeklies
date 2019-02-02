import praw
import configparser
import datetime

DATE_FILE = 'meta_last_posted'

c = configparser.ConfigParser()
c.read('config.ini')

reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

# should only be posted every 4 weeks
with open(DATE_FILE, 'r') as f:
    try:
        last_posted_str = f.read().strip()
        last_posted = datetime.date.fromisoformat(last_posted_str)

        if datetime.date.today() - last_posted < datetime.timedelta(days=28):
            print(f'Not submitted (last post: {last_posted_str})')
            exit()
    except FileNotFoundError:
        print(f"Couldn't find {DATE_FILE}, continuing")

title = datetime.date.today().strftime('Meta Thread - Month of %B %d, %Y')
content = """A monthly thread to talk about meta topics. Keep it friendly and relevant to the subreddit.

Posts here must, of course, still abide by all subreddit rules other than the no meta requirement. Keep it friendly and be respectful. Occasionally the moderators will have specific topics that they want to get feedback on, so be on the lookout for distinguished posts.

Comments that are detrimental to discussion (aka circlejerks/shitposting) are subject to removal."""

post = subreddit.submit(title, selftext=content)
post.disable_inbox_replies()
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')

with open(DATE_FILE, 'w') as f:
    f.write(datetime.date.today().isoformat())
    f.write('\n')
