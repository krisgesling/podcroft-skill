from collections import namedtuple
from typing import List

import podsearch

from mycroft.util import LOG
from mycroft.util.time import now_utc

from .subscription_manager import SubscriptionManager
from .subscription_manager.subscription import Subscription


LastUpdated = namedtuple("last_updated", ("timestamp", "titles"))


class PodcastClient:
    """A podcast client"""

    def __init__(self, config={}):
        self.sub_manager = SubscriptionManager(config)
        self.last_updated = LastUpdated(None, [])

    def subscribe_to_podcast(self, rss_url: str) -> bool:
        """Subscribes to a podcast.

        Args:
            rss_url: An RSS url that meets normal podcast specifications
        """
        return self.sub_manager.subscribe_to_podcast(rss_url)

    def unsubscribe_from_podcast(self, subscription: Subscription) -> Subscription:
        """Unsubscribe from a podcast."""
        LOG.error(subscription.title)
        return self.sub_manager.unsubscribe_from_podcast(subscription)

    def update_podcast(self, subscription: Subscription) -> bool:
        return self.sub_manager.update_subscription(subscription)

    def update_all_podcasts(self) -> List[bool]:
        LOG.info("Updating all podcast subscriptions")
        results = self.sub_manager.update_all_subscriptions()
        if any(results):
            updated_podcasts = [
                self.sub_manager.subscriptions[idx].title
                for idx, result in enumerate(results)
                if result
            ]
            self.last_updated = LastUpdated(now_utc, updated_podcasts)
            LOG.info(f"Updated {updated_podcasts}")
            return updated_podcasts

    def find_subscription(self, search_term: str) -> Subscription:
        return self.sub_manager.find_subscription(search_term)

    def search_for_new_podcast(self, search_term: str) -> List[Subscription]:
        """Search for a new podcast feed."""
        # TODO add country specific search - 2nd param
        results = podsearch.search(search_term, limit=4)
        if len(results) > 0:
            return results
