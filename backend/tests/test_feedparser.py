import pytest
import feedparser

def test_pop_rss():
    url = "https://pubs.aip.org/rss/site_1000039/1000022.xml"
    feed = feedparser.parse(url)

    # Print feed info to console
    print("\nFeed Title:", feed.feed.title)
    print(f"Feed Entries: total={len(feed.entries)}")
    for entry in feed.entries[:1]:
        print(f"- {entry.id} {entry.title} ({entry.link})")
        print(f"  {entry.summary}")
        print(f"  {entry.published}")
        print(f"  {entry.keys()}")

    # Basic assertions to validate feed structure
    assert feed.status == 200
    assert len(feed.entries) > 0


def test_apj_rss():
    url = "https://iopscience.iop.org/journal/rss/0004-637X"
    feed = feedparser.parse(url)

    # Print feed info to console
    print("\nFeed Title:", feed.feed.title)
    print(f"Feed Entries: total={len(feed.entries)}")
    for entry in feed.entries[:1]:
        print(f"- {entry.id} {entry.title} ({entry.link})")
        print(f"  {entry.authors}")
        print(f"  {entry.summary}")
        print(f"  {entry.updated}")
        print(f"  {entry.keys()}")

    # Basic assertions to validate feed structure
    assert feed.status == 200
    assert len(feed.entries) > 0



def test_ncomms_rss():
    url = "https://www.nature.com/subjects/earth-and-environmental-sciences/ncomms.rss"
    feed = feedparser.parse(url)

    # Print feed info to console
    print("\nFeed Title:", feed.feed.title)
    print(f"Feed Entries: total={len(feed.entries)}")
    for entry in feed.entries[:1]:
        print(f"- {entry.id} {entry.title} ({entry.link})")
        print(f"  {entry.published}")
        print(f"  {entry.summary}")
        print(f"  {entry.keys()}")

    # Basic assertions to validate feed structure
    assert feed.status == 200
    assert len(feed.entries) > 0



def test_aguadvns_rss():
    url = "https://agupubs.onlinelibrary.wiley.com/action/showFeed?jc=2576604x&type=etoc&feed=rss"
    feed = feedparser.parse(url)

    # Print feed info to console
    print("\nFeed Title:", feed.feed.title)
    print(f"Feed Entries: total={len(feed.entries)}")
    for entry in feed.entries[:1]:
        print(f"- {entry.id} {entry.title} ({entry.link})")
        print(f"  {entry.authors}")
        print(f"  {entry.summary}")
        print(f"  {entry.published}")
        print(f"  {entry.keys()}")

    # Basic assertions to validate feed structure
    assert feed.status == 200
    assert len(feed.entries) > 0