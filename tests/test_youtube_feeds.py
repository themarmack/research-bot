"""Deterministic tests for the YouTube channel-feed helpers.

These decide WHICH channel gets polled, so a wrong answer is silent: the digest
fills with a plausible-looking but incorrect channel's videos. The
featured-channel regression test below encodes a real mis-resolution observed
while building the roster.
"""
import pytest

from _util import SKILLS, load_module

yt = load_module(SKILLS / "voices-watcher" / "youtube_feeds.py", "youtube_feeds")

KARPATHY = "UCXUPKJO5MZQN11PqgIvyuvQ"
MLST = "UCMLtBahI5DMrt0NPvDSoIRQ"


# --- channel id recognition -------------------------------------------------

def test_is_channel_id_accepts_valid():
    assert yt.is_channel_id(KARPATHY)


@pytest.mark.parametrize(
    "value",
    [
        "",
        None,
        "UC",
        "XCXUPKJO5MZQN11PqgIvyuvQ",          # wrong prefix
        "UCXUPKJO5MZQN11PqgIvyuv",           # 21 chars after UC
        "UCXUPKJO5MZQN11PqgIvyuvQQ",         # 23 chars after UC
        "https://www.youtube.com/channel/" + KARPATHY,  # a URL, not a bare id
    ],
)
def test_is_channel_id_rejects(value):
    assert not yt.is_channel_id(value)


# --- URL -> channel id ------------------------------------------------------

def test_channel_id_from_canonical_url():
    assert yt.channel_id_from_url(f"https://www.youtube.com/channel/{KARPATHY}") == KARPATHY


def test_channel_id_from_existing_feed_url():
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={KARPATHY}"
    assert yt.channel_id_from_url(url) == KARPATHY


def test_channel_id_from_bare_id():
    assert yt.channel_id_from_url(KARPATHY) == KARPATHY


def test_channel_id_tolerates_surrounding_whitespace():
    assert yt.channel_id_from_url(f"  https://www.youtube.com/channel/{KARPATHY}  ") == KARPATHY


def test_handle_url_is_not_resolvable_offline():
    """@handle URLs carry no id — the caller must fetch and resolve."""
    assert yt.channel_id_from_url("https://www.youtube.com/@AndrejKarpathy") is None


def test_non_youtube_url_rejected():
    assert yt.channel_id_from_url(f"https://evil.example.com/channel/{KARPATHY}") is None


def test_trailing_path_after_channel_id_still_resolves():
    url = f"https://www.youtube.com/channel/{KARPATHY}/videos"
    assert yt.channel_id_from_url(url) == KARPATHY


# --- feed URL construction --------------------------------------------------

def test_feed_url_for_channel_url():
    assert yt.feed_url_for(f"https://www.youtube.com/channel/{KARPATHY}") == (
        f"https://www.youtube.com/feeds/videos.xml?channel_id={KARPATHY}"
    )


def test_feed_url_is_idempotent_on_feed_url():
    feed = f"https://www.youtube.com/feeds/videos.xml?channel_id={KARPATHY}"
    assert yt.feed_url_for(feed) == feed


def test_feed_url_none_for_unresolvable():
    assert yt.feed_url_for("https://www.youtube.com/@AndrejKarpathy") is None
    assert yt.feed_url_for("") is None
    assert yt.feed_url_for(None) is None


def test_channel_url_for_roundtrip():
    assert yt.channel_id_from_url(yt.channel_url_for(KARPATHY)) == KARPATHY


def test_channel_url_for_rejects_junk():
    with pytest.raises(ValueError):
        yt.channel_url_for("not-a-channel")


# --- handle resolution (the fragile step) -----------------------------------

def test_resolve_prefers_canonical_over_featured_channel():
    """Regression: a channel page embeds FEATURED channels' ids too.

    Taking the first bare "channelId" match returned a neighbouring channel for
    5 of 6 channels during roster construction — silently, with no error. The
    canonical link is the channel's own id and must win.
    """
    html = f"""
    <html><head>
      <script>{{"channelId":"UCwwwwwwwwwwwwwwwwwwwwww","featured":true}}</script>
      <link rel="canonical" href="https://www.youtube.com/channel/{MLST}">
    </head></html>
    """
    assert yt.resolve_channel_id(html) == MLST


def test_resolve_falls_back_to_external_id():
    html = f'<script>{{"externalId":"{MLST}","channelId":"UCwwwwwwwwwwwwwwwwwwwwww"}}</script>'
    assert yt.resolve_channel_id(html) == MLST


def test_resolve_returns_none_rather_than_guessing():
    """A bare channelId is NOT enough — better no answer than the wrong one."""
    html = '<script>{"channelId":"UCwwwwwwwwwwwwwwwwwwwwww"}</script>'
    assert yt.resolve_channel_id(html) is None


def test_resolve_handles_empty_input():
    assert yt.resolve_channel_id("") is None
    assert yt.resolve_channel_id(None) is None


# --- feed parsing -----------------------------------------------------------

FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"
      xmlns="http://www.w3.org/2005/Atom">
 <title>Neel Nanda</title>
 <entry>
  <id>yt:video:e0V0pYh4M7M</id>
  <yt:videoId>e0V0pYh4M7M</yt:videoId>
  <title>How Aligned Is Claude? A Live Review of the Opus 4.5 System Card</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=e0V0pYh4M7M"/>
  <published>2026-08-20T17:00:00+00:00</published>
 </entry>
 <entry>
  <id>yt:video:AAAAAAAAAAA</id>
  <yt:videoId>AAAAAAAAAAA</yt:videoId>
  <title>Second video</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=AAAAAAAAAAA"/>
  <published>2026-08-18T09:00:00+00:00</published>
 </entry>
</feed>
"""


def test_parse_feed_extracts_items():
    items = yt.parse_feed(FEED)
    assert len(items) == 2
    first = items[0]
    assert first["video_id"] == "e0V0pYh4M7M"
    assert first["title"].startswith("How Aligned Is Claude?")
    assert first["url"] == "https://www.youtube.com/watch?v=e0V0pYh4M7M"
    assert first["published"] == "2026-08-20T17:00:00+00:00"
    assert first["channel_title"] == "Neel Nanda"


def test_parse_feed_preserves_order():
    assert [i["video_id"] for i in yt.parse_feed(FEED)] == ["e0V0pYh4M7M", "AAAAAAAAAAA"]


def test_parse_feed_empty_channel():
    empty = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom"><title>Nobody</title></feed>'
    )
    assert yt.parse_feed(empty) == []


def test_parse_feed_skips_entries_missing_id_or_link():
    partial = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"
          xmlns="http://www.w3.org/2005/Atom">
     <title>Partial</title>
     <entry><title>No video id or link</title></entry>
     <entry>
      <yt:videoId>BBBBBBBBBBB</yt:videoId>
      <title>Has both</title>
      <link rel="alternate" href="https://www.youtube.com/watch?v=BBBBBBBBBBB"/>
     </entry>
    </feed>
    """
    items = yt.parse_feed(partial)
    assert [i["video_id"] for i in items] == ["BBBBBBBBBBB"]


def test_parse_feed_raises_on_malformed_xml():
    """Stop and report — never return [] for a broken feed."""
    import xml.etree.ElementTree as ET

    with pytest.raises(ET.ParseError):
        yt.parse_feed("<feed><unclosed>")


# --- org-row convention -----------------------------------------------------

@pytest.mark.parametrize("role", ["AI security (org)", "security conference (org)", "AI vendor (ORG)"])
def test_is_org_role_true(role):
    assert yt.is_org_role(role)


@pytest.mark.parametrize("role", ["AI researcher", "AI security research", "", None, "org lead"])
def test_is_org_role_false(role):
    assert not yt.is_org_role(role)
