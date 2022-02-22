from typing import List

import podsearch

from mycroft.util import LOG

from .subscription_manager import SubscriptionManager
from .subscription_manager.subscription import Subscription


class PodcastClient:
    """A podcast client"""

    def __init__(self, config={}):
        self.sub_manager = SubscriptionManager(config)

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

    def find_subscription(self, search_term: str) -> Subscription:
        return self.sub_manager.find_subscription(search_term)

    def search_for_new_podcast(self, search_term: str) -> List[Subscription]:
        """Search for a new podcast feed."""
        # TODO add country specific search - 2nd param
        results = podsearch.search(search_term, limit=4)
        if len(results) > 0:
            return results
