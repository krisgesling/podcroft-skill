from dataclasses import dataclass

from mycroft.util import LOG

from ..util import get_ms_from_hms


@dataclass(frozen=True)
class Episode:
    title: str
    subtitle: str
    summary: str
    author: str
    image: str
    stream_url: str
    mime_type: str
    show_notes_url: str
    duration: int
    episode_number: int


def create_episode_list(entries):
    """Create a list of episodes from an RSS entries list."""
    return [create_episode(entry) for entry in entries]


def create_episode(episode):
    """Create an episode from an individual RSS entry."""
    stream = None
    for link in episode["links"]:
        if link["rel"] == "enclosure":
            stream = link

    duration = get_duration_of_episode(episode, stream)

    return Episode(
        title=episode.get("title", ""),
        subtitle=episode.get("subtitle"),
        summary=episode.get("summary"),
        show_notes_url=episode.get("link"),
        image=episode.get("image", {}).get("href"),
        author=episode.get("author"),
        episode_number=episode.get("itunes_episode"),
        stream_url=stream.get("href"),
        mime_type=stream.get("type"),
        duration=duration,
    )


def get_duration_of_episode(episode, stream):
    """Determine the duration of an episode.

    This can be reported in multiple locations depending on the RSS feed.

    Returns:
        duration in ms, or -1 if no duration can be found.
    """
    duration = -1
    duration_str = stream.get("length") or episode.get("itunes_duration", "")
    if ":" in duration_str:
        duration = get_ms_from_hms(duration_str)
    else:
        try:
            duration = int(duration_str)
        except ValueError:
            LOG.error(f"Cannot determine stream length from: {duration_str}")

    return duration
