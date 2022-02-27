import os
import random
from typing import List

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
            create_subscription_from_json(entry["self"], entry)
            for entry in self.subscription_db.entries
        ]

    def get_rss_feed(self, rss_url: str) -> dict:
        """Fetch an RSS feed"""
        data = feedparser.parse(rss_url)
        if None in (data.get("feed"), data.get("entries")):
            return None
        else:
            return data

    def subscribe_to_podcast(self, rss_url: str) -> Subscription:
        """Subscribes to a podcast based on the given RSS feed."""
        if rss_url == "" or not isinstance(rss_url, str):
            return None
        data = self.get_rss_feed(rss_url)
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

    def update_subscription(self, subscription: Subscription, sub_index) -> bool:
        """Fetch new data for a podcast.

        Args:
            The subscription to update.
            Index of the subscription in self.subscriptions

        Returns:
            If new data was available.

        Raises:
            #TODO decide error type: if url is no longer available
        """
        if self.subscriptions[sub_index] is not subscription:
            LOG.error(f"Incorrect index given for {subscription.title}")
            return False
        rss_url = subscription.rss_url
        data = self.get_rss_feed(rss_url)
        url_updated_timestamp = data.get("feed", {}).get("published")
        local_updated_timestamp = subscription.full_data.get("feed", {}).get(
            "published"
        )
        if None in (url_updated_timestamp, local_updated_timestamp):
            LOG.error(f"Could not find last updated timestamp for {subscription.title}")
        if url_updated_timestamp == local_updated_timestamp:
            return False
        updated_subscription = create_subscription_from_json(rss_url, data)
        self.subscriptions[sub_index] = updated_subscription
        self.subscription_db.replace_entry(rss_url, data)
        return True

    def update_all_subscriptions(self) -> List[bool]:
        """Perform an update on all subscribed podcasts.

        Returns:
            List of whether each subscription was updated.
        """
        results = [
            self.update_subscription(sub, idx)
            for idx, sub in enumerate(self.subscriptions)
        ]
        return results

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
        full_data=json,
    )
