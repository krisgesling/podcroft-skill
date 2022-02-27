from mycroft import MycroftSkill, intent_handler
from mycroft.skills.common_play_skill import CommonPlaySkill
from mycroft.util.format import join_list
from mycroft.util.parse import extract_datetime

from .podcast_client import PodcastClient

HOUR = 3600
DAY = 86400


class Podcroft(CommonPlaySkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.init_podcast_client()
        self.settings_change_callback = self.on_settings_changed
        first_update_time, _ = extract_datetime("2am tomorrow")
        self.schedule_repeating_event(
            self.client.update_all_podcasts, when=first_update_time, frequency=DAY
        )

    def init_podcast_client(self):
        config = {"storage_dir": self.file_system.path}
        self.client = PodcastClient(config)

    def on_settings_changed(self):
        """Callback executed anytime settings change."""
        self.handle_subscribe_from_settings()

    @intent_handler("play-latest-episode.intent")
    def handle_podcroft(self, message):
        podcast_name = message.data.get("podcast_name")
        podcast = self.client.find_subscription(podcast_name)
        if len(podcast.episodes) <= 0:
            self.log.error(f"No episodes found in {podcast.title}")
        episode = podcast.episodes[0]
        self.speak_dialog(
            "fetching-episode",
            {"podcast_title": podcast.title, "episode_title": episode.title},
            wait=True,
        )
        self.play_episode(episode)

    def play_episode(self, episode):
        self.log.info(episode.stream_url)
        self.audioservice.play((episode.stream_url, episode.mime_type))

    def CPS_start(self, _, data):
        """Handle request from Common Play System to start playback."""
        pass

    def CPS_match_query_phrase(self, phrase: str) -> tuple((str, float, dict)):
        """Respond to Common Play Service query requests."""
        pass

    ##########################################################################
    #### SUBSCRIPTION MANAGEMENT
    ##########################################################################
    @intent_handler("subscribe-by-name.intent")
    def handle_subscribe_by_name(self, message=None):
        rss_url = None
        search_term = message.data["podcast_title"]
        results = self.client.search_for_new_podcast(search_term)
        if results is None:
            self.speak_dialog("could-not-find", {"title": search_term})
            return
        self.show_single_podcast(results[0].name, results[0].image, persist=True)
        confirm = self.ask_yesno(
            "did-you-mean-title-and-author",
            {"title": results[0].name, "author": results[0].author},
        )
        self.gui.release()
        if confirm == "yes":
            rss_url = results[0].feed
        else:
            self.speak_dialog("i-also-found")
            remaining_titles = [result.name for result in results[1:]]
            selection = self.ask_selection(
                remaining_titles, "did-you-mean-one-of-these"
            )
            for result in results:
                if result.name == selection:
                    rss_url = result.feed

        if rss_url is not None:
            subscription = self.client.subscribe_to_podcast(rss_url)
            if subscription:
                self.speak_dialog(
                    "subscribed-to-new-podcast", {"title": subscription.title}
                )

    @intent_handler("subscribe-from-settings.intent")
    def handle_subscribe_from_settings(self, message=None):
        subscription_url = self.settings.get("subscription_url", "")
        subscription = self.client.subscribe_to_podcast(subscription_url)
        self.speak_dialog("subscribed-to-new-podcast", {"title": subscription.title})

    @intent_handler("unsubscribe-from-podcast.intent")
    def handle_unsubscribe_from_podcast(self, message=None):
        search_title = message.data.get("podcast_title")
        subscription = self.client.find_subscription(search_title)
        self.log.error(subscription.title)
        subscription = self.client.unsubscribe_from_podcast(subscription)
        self.speak_dialog("unsubscribed-from-podcast", {"title": subscription.title})

    @intent_handler("update-podcasts.intent")
    def handle_update_podcasts_request(self, message=None):
        """Update all podcast feeds.

        Example utterances:
            - Fetch new episodes
            - Update all of my podcasts
        """
        self.speak_dialog("fetching-new-episodes")
        updated_podcasts = self.client.update_all_podcasts()
        if updated_podcasts is None:
            self.speak_dialog("no-updates-found")
            return
        self.log.info(f"Updated podcasts: {updated_podcasts}")
        if len(updated_podcasts) > 3:
            self.speak_dialog(
                "updated-podcasts-report-by-number", {"number": len(updated_podcasts)}
            )
        else:
            self.speak_dialog(
                "updated-podcasts-report-by-name",
                {"podcast_titles": join_list(updated_podcasts, "and")},
            )

    ##########################################################################
    #### SHOW PAGES
    ##########################################################################
    def show_single_podcast(
        self, title: str = "", image: str = "", persist: bool = False
    ):
        self.gui["title"] = title
        self.gui["imgLink"] = image
        self.gui.show_page("SinglePodcastTitle.qml", override_idle=persist)


def create_skill():
    return Podcroft()
