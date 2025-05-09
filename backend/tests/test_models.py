import pytest
from ..models import (RSS_Journal, RSSItem)
from ..rss import retrieve
from yaml import safe_load

RSS_YAML_PATH = "backend/rss/rss.yml"

def test_rss_yaml():
    """
    Test the RSS YAML configuration
    """
    # load yaml
    with open(RSS_YAML_PATH, "r", encoding="utf-8") as fp:
        rss_yml = safe_load(fp.read())
    
    for journal_key, journal_obj_raw in rss_yml.items():
        print(f"======= {journal_key} =======")

        journal_obj = RSS_Journal.model_validate(journal_obj_raw)
        new_items = retrieve(journal_obj)
        print(f"new_items: {new_items}")

        print("==============")

