from dataclasses import dataclass

from .episode import create_episode_list


@dataclass(frozen=True)
class Subscription:
    title: str
    subtitle: str
    summary: str
    image: str
    rss_url: str
    homepage_url: str
    author: str
    episode_dict: dict
    full_data: dict

    @property
    def episodes(self):
        return create_episode_list(self.episode_dict)
