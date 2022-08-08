import configparser
import time
import random
import sys
from datetime import datetime, date, timezone, timedelta

from menuupdater import SubredditMenuUpdater, get_reddit_instance

name = 'Casual Discussion Fridays'
short_name = 'Casual Disc Fridays'
author = 'AutoModerator'
config_file = 'config.ini'

# First wait for new thread to go up and update links (standard)
SubredditMenuUpdater(name=name,
                     short_name=short_name,
                     author=author,
                     config_file=config_file)

# Then the CDF-specific stuff
c = configparser.ConfigParser()
c.read('config.ini')
reddit = get_reddit_instance(c['Auth'])
subreddit = reddit.subreddit(c['Options']['subreddit'])

# Step 0: get new and old CDF
search_str = f'{name.lower()} author:{author}'
print(f'Search query: {search_str}')
cdfs = subreddit.search(search_str, sort='new')

while True:
    cdf = next(cdfs)
    created_ts = datetime.fromtimestamp(cdf.created_utc, timezone.utc)
    if created_ts > datetime.now(timezone.utc) - timedelta(days=1): # today
        new_cdf = cdf
    elif created_ts < datetime.now(timezone.utc) - timedelta(days=6): # last week
        old_cdf = cdf
        break

print(f'Found new CDF id {new_cdf.id} "{new_cdf.title}"')
print(f'Found old CDF id {old_cdf.id} "{old_cdf.title}"')


# Step 1: Notify old CDF that the new CDF is up
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
Don't take the shitpost too far — but have fun!

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
