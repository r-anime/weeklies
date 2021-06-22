import praw
import configparser
import datetime

from menuupdater import SubredditMenuUpdater

c = configparser.ConfigParser()
c.read('config.ini')
reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])
flair_id = c['Options']['flair_meta_id']

title = datetime.date.today().strftime('Meta Thread - Month of %B %d, %Y')
content = """A monthly thread to talk about meta topics. Keep it friendly and relevant to the subreddit.

Posts here must, of course, still abide by all subreddit rules other than the no meta requirement. Keep it friendly and be respectful. Occasionally the moderators will have specific topics that they want to get feedback on, so be on the lookout for distinguished posts.

Comments that are detrimental to discussion (aka circlejerks/shitposting) are subject to removal."""

post = subreddit.submit(title, selftext=content, flair_id=flair_id, flair_text='Meta')
post.disable_inbox_replies()
post.mod.suggested_sort(sort='new')
post.mod.distinguish()
post.mod.sticky()

print(f'Submitted {post.title}')

# Update links
SubredditMenuUpdater(name='Monthly Meta Thread',
                     short_name='Monthly Meta Thread',
                     author='AnimeMod',
                     config_file='config.ini')
