import praw
import configparser
import time
import random
import sys
from datetime import datetime, date, timezone, timedelta

c = configparser.ConfigParser()
c.read('config.ini')
reddit = praw.Reddit(**c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

# Step 0: get old CDF
search_str = 'Casual Discussion Fridays'
#search_str = 'Casual Discussion Fridays author:AutoModerator'
cdfs = subreddit.search(search_str, sort='new')
while True:
    old_cdf = next(cdfs)
    created_ts = datetime.fromtimestamp(old_cdf.created_utc, timezone.utc)
    if created_ts < datetime.now(timezone.utc) - timedelta(days=6):
        break

print(f'Found old CDF id {old_cdf.id} "{old_cdf.title}"')

# Step 1: Create new CDF
title = date.today().strftime('Casual Discussion Fridays - Week of %B %d, %Y')
content = """
This is a weekly thread to get to know /r/anime's community. Talk about your day-to-day life, share your hobbies, or make small talk with your fellow anime fans.

Although this is a place for off-topic discussion, there are a few rules to keep in mind:

1. Be courteous and respectful of other users.

2. Discussion of religion, politics, depression, and other similar topics will be moderated due to their sensitive nature. While we encourage users to talk about their daily lives and get to know others, this thread is not intended for extended discussion of the aforementioned topics or for emotional support.

3. Roleplaying is not allowed. This behaviour is not appropriate as it is obtrusive to uninvolved users.

4. No meta discussion. If you have a meta concern, please raise it in the Monthly Meta Thread and the moderation team would be happy to help.

5. All r/anime rules, other than the anime-specific requirement, should still be followed.
"""
new_cdf = subreddit.submit(title, selftext=content)
new_cdf.disable_inbox_replies()
new_cdf.mod.distinguish()
new_cdf.mod.sticky()

print(f'Submitted {new_cdf.title}')

# Step 1.5: Notify old CDF that the new CDF is up
notify_comment = old_cdf.reply(f'''
Hello CDF users! Since it is Friday, the new CDF is now live. Please follow
[this link]({new_cdf.permalink}) to move on to the new thread.

[](#heartbot "And don't forget to be nice to new users!")

A quick note: this thread will remain open for one hour so that you can finish
your conversations. Please **do not** use this thread for spamming or other
undesirable behavior. Excessive violations will result in sanctions.
''')
notify_comment.disable_inbox_replies()
notify_comment.mod.distinguish()

print(f'Posted notify comment {notify_comment.id} in old CDF')

# Step 2: Lock old CDF
print('Going to sleep for 3600 seconds...')
sys.stdout.flush()
time.sleep(3600)
print('Waking up. Locking old CDF')

old_cdf.mod.lock()
print('Old CDF thread has been locked')
last_comment = old_cdf.reply(f'''
This thread has been locked.
We will see you all in the new Casual Discussion Fridays thread,
which you can find [here]({new_cdf.permalink}).

Reminder to keep the new discussion *welcoming* and be mindful of new users.
Don't take the shitpost too far - but have fun!

[](#bot-chan)
''')
last_comment.disable_inbox_replies()
last_comment.mod.distinguish(sticky=True)

print(f'Last comment {last_comment.id} posted')

# Step 3: sort new CDF by new
print('Going to sleep for 3600 seconds...')
sys.stdout.flush()
time.sleep(3600)

print("Waking up. Setting new CDF thread sorting to 'new'")
new_cdf.mod.suggested_sort(sort='new')

print('Job complete. Goodbye.')
