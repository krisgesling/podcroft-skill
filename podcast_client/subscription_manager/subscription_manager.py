import os
import random

import feedparser

from mycroft.util import LOG
from mycroft.util.parse import match_one

from .subscription import Subscription
from ..db import Database


class SubscriptionManager:
    """Manage podcast feed subscriptions."""

    def __init__(self, config={}):
        subscription_db_path = os.path.join(config["storage_dir"], "db")
        self.subscription_db = Database(
            config={
                "storage_dir": subscription_db_path,
                "db_filename": "subscriptions.db",
            }
        )
        self.subscriptions = [
            create_subscription_from_json(entry['self'], entry)
            for entry in self.subscription_db.entries
        ]

    def subscribe_to_podcast(self, rss_url: str) -> Subscription:
        """Subscribes to a podcast based on the given RSS feed."""
        if rss_url == "" or not isinstance(rss_url, str):
            return None
        data = feedparser.parse(rss_url)
        LOG.info(f"Subscribing to: {data.feed.title}")
        LOG.info(data.feed.description)
        subscription = create_subscription_from_json(rss_url, data)
        if subscription in self.subscriptions:
            LOG.error(f"Already subscribed to {subscription.title}")
        else:
            self.subscriptions.append(subscription)
            self.subscription_db.add_entry(rss_url, data)
        return subscription

    def unsubscribe_from_podcast(self, subscription: Subscription) -> Subscription:
        """Unsubscribe from a podcast."""
        # if rss_url == "" or not isinstance(rss_url, str):
        #     return None
        # subscription = self.find_subscription_by_rss(rss_url)
        LOG.error(subscription.title)
        self.subscriptions.remove(subscription)
        self.subscription_db.remove_entry(subscription.rss_url)
        return subscription

    def find_subscription(self, search_term: str) -> Subscription:
        """Find the feed requested by the user.

        Currently this only searches by podcast title.
        """
        titles = [subscription.title for subscription in self.subscriptions]
        selection, confidence = match_one(search_term, titles)
        idx = titles.index(selection)
        return self.subscriptions[idx]

    def find_subscription_by_rss(self, rss_url: str) -> Subscription:
        """Find an existing subscription by its RSS url."""
        for subscription in self.subscriptions:
            if subscription.rss_url == rss_url:
                return subscription

    def get_random_feed(self) -> Subscription:
        """Get any feed from the subscribed podcasts."""
        return random.choice(self.subscriptions)


def create_subscription_from_json(rss_url: str, json: dict) -> Subscription:
    """Create a Subscription from stored JSON object.

    It is currently assumed that this object was created from an RSS feed.
    """
    info = json.get("feed")
    if info is None:
        return

    return Subscription(
        title=info.get("title", ""),
        subtitle=info.get("subtitle"),
        summary=info.get("summary"),
        image=info.get("image", {}).get("href"),
        rss_url=rss_url,
        homepage_url=info.get("link"),
        author=info.get("author"),
        episode_dict=json.get("entries", []),
    )
