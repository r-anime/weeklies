import sys

import time
from datetime import datetime, timezone, timedelta

import praw
import configparser
import re


class SubredditMenuUpdater:
    def __init__(self, name, short_name, author, config_file='config.ini', debug=False):
        """
        Update the subreddit menu to the most recent post with <name>
        Used to replace links for weekly megathreads

        This script is supposed to run *at the same time* as the thread to
        update is posted. A timeout guarantees that if the post is not found
        soon, the script will stop with failure.

        The Reddit mod account, subreddit, and various script settings are
        configured in a static file (default `config.ini`).

        :param name: name of the post as written in the title and menu
        :param short_name: name to use in redesign topbar (max 20 characters)
        :param author: account from which the post was submitted
        :param config_file: path to the config file
        :param debug: if True, no change will be made to the subreddit
        """

        self._log(f'Started running subreddit menu updater for {name}')
        self._load_config(config_file)

        post = self._find_post(name, author)
        self._update_menus(name, post, debug=debug)
        self._update_redesign_menus(name, short_name, post, debug=debug)

    def _load_config(self, config_file):
        """
        Load the configuration for the script and PRAW
        Sets the variables `self.config`, `self.reddit` and `self.subreddit`

        :param config_file: path to the config file
        """
        c = configparser.ConfigParser()
        c.read(config_file)
        self.config = c
        self.reddit = praw.Reddit(**c['Auth'])
        self.subreddit = self.reddit.subreddit(c['Options']['subreddit'])

    def _find_post(self, name, author):
        search_str = f'{name} author:{author}'.lower()
        search_start_time = time.time()
        search_timeout = int(self.config['Options']['search_timeout'])

        self._log(f"Started search with query '{search_str}'")
        while True:
            post = next(self.subreddit.search(search_str, sort='new'), None)
            if post is not None:
                post_timestamp = datetime.fromtimestamp(post.created_utc, timezone.utc)
                if post_timestamp > datetime.now(timezone.utc) - timedelta(days=6):
                    # guarantees that the post found was created in the past day
                    self._log(f'Post found {post.permalink}')
                    return post

            if time.time() - search_start_time > search_timeout:
                raise TimeoutError('Post not found')
            time.sleep(5)

    def _update_menus(self, name, post, debug=False):
        """
        Updates the sidebar text by replacing links to `name` with a permalink
        to `post`. Links formatting is defined by config.

        For example, the default format for links is `'[{name}](.*)'`

        :param name: name of the link to format
        :param post: post which should be linked to
        """
        self._log("Updating menus on old Reddit")

        pattern_match_base = self.config['Options']['link_regex']
        pattern_match = pattern_match_base.format(name=name)

        pattern_replace_base = self.config['Options']['link_format']
        pattern_replace = pattern_replace_base.format(name=name, link=post.shortlink)

        sidebar = self.subreddit.wiki["config/sidebar"]
        sidebar_text = sidebar.content_md
        sidebar_updated_text = self._replace_text(pattern_match,
                                                  pattern_replace,
                                                  sidebar_text)

        if sidebar_updated_text is None:
            self._log('No change necessary')
        elif debug:
            self._log('Running in debug mode, no change was made to sidebar')
        else:
            sidebar.edit(content=sidebar_updated_text,
                         reason=f'Changed link for {name}')
            self._log('Changes saved to sidebar')

    def _update_redesign_menus(self, name, short_name, post, debug=False):
        """
        Updates the menu and widget text on Redesign by replacing links to
        `name` with a permaling to `post`. Links formatting is identical to the
        formatting used on old Reddit.

        :param name: name of the link to format
        :param short_name: name of the link to use in topbar menu (max 20 characters)
        :param post: post which should be linked to
        """
        self._log("Updating menus on Redesign")

        assert len(short_name) <= 20

        topmenu = self._get_updated_redesign_topmenu(short_name, post.shortlink)
        if topmenu is None:
            self._log('Error updating topmenu')
        elif debug:
            self._log('Running in debug mode, no change was made to top menu')
        else:
            topmenu.mod.update(data=list(topmenu))
            self._log('Topbar menu updated')

        pattern_match_base = self.config['Options']['link_regex']
        pattern_match = pattern_match_base.format(name=name)

        pattern_replace_base = self.config['Options']['link_format']
        pattern_replace = pattern_replace_base.format(name=name, link=post.shortlink)

        sidemenu = self._get_redesign_sidemenu(name)
        sidemenu_text = sidemenu.text
        sidemenu_updated_text = self._replace_text(pattern_match,
                                                   pattern_replace,
                                                   sidemenu_text)

        if sidemenu_updated_text is None:
            self._log('No change necessary')
        elif debug:
            self._log('Running in debug mode, no change was made to side menu')
        else:
            sidemenu.mod.update(text=sidemenu_updated_text)
            self._log('Sidebar widget updated')

    def _get_updated_redesign_topmenu(self, name, new_url):
        """
        Update the menu by replacing links labeled `name` with `new_url` and
        return the updated menu. Updates are *not* reflected to the subreddit
        by calling this method.

        :param name: text of the menulink to update
        :param new_url: replacement url
        """
        menu = self.subreddit.widgets.topbar[0]
        assert isinstance(menu, praw.models.Menu)

        for item in menu:
            if isinstance(item, praw.models.MenuLink):
                if item.text == name:
                    self._log(f"Found replaceable MenuLink: {item.text}")
                    item.url = new_url
            elif isinstance(item, praw.models.Submenu):
                for subitem in item:
                    if isinstance(subitem, praw.models.MenuLink):
                        if subitem.text == name:
                            self._log(f"Found replaceable MenuLink: {item.text}")
                            subitem.url = new_url
                    else:
                        self._log(f'Wrong type found searching for MenuLink: {item.__class__}')
            else:
                self._log(f'Wrong type found searching for MenuLink: {item.__class__}')

        return menu

    def _get_redesign_sidemenu(self, name):
        """
        Return the sidebar widget containing a link to `name`.

        :param name: name of the link to update
        """
        sidebar = self.subreddit.widgets.sidebar

        pattern_match_base = self.config['Options']['link_regex']
        pattern_match = pattern_match_base.format(name=name)

        for widget in sidebar:
            if isinstance(widget, praw.models.TextArea):
                matches = re.findall(pattern_match, widget.text)
                if matches:
                    self._log(f"Found matching side widget '{widget.shortName}'")
                    return widget

        self._log("Found no sidebar widget with replaceable match")
        return None

    def _replace_text(self, pattern_match, pattern_replace, text):
        matches = re.findall(pattern_match, text)
        if not matches:
            self._log('Found no replaceable match')
            return None

        self._log('Found replaceable matches\n' +
                  f'\t\t\tOld text: {" // ".join(matches)}\n' +
                  f'\t\t\tNew text: {pattern_replace}')

        text_replaced = re.sub(pattern_match, pattern_replace, text)
        return text_replaced

    def _log(self, message):
        """
        Dedicted logger. Format prints to stdout.
        """
        script_name = sys.argv[0]
        script_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        preamble = f'[{script_name}] ({script_time})'
        print(preamble, message)
