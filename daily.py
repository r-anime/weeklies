import configparser
import re
from datetime import datetime, timezone, timedelta

from menuupdater import SubredditMenuUpdater, get_reddit_instance

name = 'Anime Questions, Recommendations, and Discussion'
short_name = 'Daily Megathread'
author = 'AnimeMod'
config_file = 'config.ini'

# First wait for new thread to go up and update links (standard)
SubredditMenuUpdater(name=name,
                     short_name=short_name,
                     author=author,
                     config_file=config_file)

# Daily Thread Specific Stuff
c = configparser.ConfigParser()
c.read('config.ini')
reddit = get_reddit_instance(c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

# Step 0: get new and old Daily
search_str = f'title:"{name.lower()}" author:{author}'
print(f'Search query: {search_str}')
threads = subreddit.search(search_str, sort='new')

while True:
    thread = next(threads)
    created_ts = datetime.fromtimestamp(thread.created_utc, timezone.utc)
    if created_ts > datetime.now(timezone.utc) - timedelta(hours=6):  # today
        new_daily = thread
    elif datetime.now(timezone.utc) - timedelta(days=2) < created_ts < datetime.now(timezone.utc) - timedelta(days=1):
        old_daily = thread
        break

print(f'Found new daily id {new_daily.id} "{new_daily.title}"')
print(f'Found old daily id {old_daily.id} "{old_daily.title}"')


# Step 1: Notify old daily that the new daily is up
notify_comment = old_daily.reply(f'''
Hello /r/anime, a new daily thread has been posted! Please follow
[this link]({new_daily.permalink}) to move on to the new thread
or [search for the latest thread](/r/{subreddit}/search?q=flair%3ADaily&restrict_sr=on&sort=new).

[](#heartbot "And don't forget to be nice to new users!")
''')
notify_comment.disable_inbox_replies()
notify_comment.mod.distinguish(sticky=True)

print(f'Posted notify comment {notify_comment.id} in old daily')

# Step 2: Update old daily body with link to new one
old_daily.edit(body=re.sub(r"\[Next Thread »]\(.*?\)", f"[Next Thread »]({new_daily.permalink})", old_daily.selftext))

print('Updated old daily body with link to new')

# Step 3: Add sticky comment for the new thread (if it exists)
sticky_comment_wiki = subreddit.wiki["daily_thread/sticky_comment"]
try:
    sticky_comment_text = sticky_comment_wiki.content_md.strip()
except:
    sticky_comment_text = ""

if sticky_comment_text:
    new_sticky_comment = new_daily.reply(sticky_comment_text)
    new_sticky_comment.mod.distinguish(sticky=True)
    print('Posted sticky comment to new thread')
else:
    print('No sticky comment for new thread')

# Step 4: Rewrite links
original_text = new_daily.selftext
# Change redd.it/<id> links to relative /comments/<id>
updated_text = re.sub(r"https?://(?:www\.)?redd\.it/(\w+)/?", r"/comments/\g<1>", original_text)
# Keep redesign/mobile image embed after edit
updated_text = re.sub(r"\[(.*?)]\(https://preview\.redd\.it/(\w+)\..*?\)", r'![img](\g<2> "\g<1>")', updated_text)
new_daily.edit(body=updated_text)

print('Updated new daily body with relative links to posts')

# Step 5: Sort by new (since it's broken on reddit's end right now)
new_daily.mod.suggested_sort(sort='new')

print('Job complete. Goodbye.')
