from sqlmodel import SQLModel, Field, Session, select
import feedparser
from datetime import datetime

from .models import RSS_Journal, RSSItem, DateFormat
from .logger import custom_logger
from .config import AppSettings, get_config

config = get_config()
logger = custom_logger(__name__, debug=config.DEBUG)

def retrieve(journal: RSS_Journal, session: Session | None = None, update_duplicate: bool = True
    ) -> list[RSSItem]:
        """ """
        # TODO separate feed stream, use robust httpx request
        # direct use cause 403 for PoP

        # feed_stream = httpx.get(journal.feed)
        # logger.info(f"Feed stream: {feed_stream.text}")
        # feed_objs = feedparser.parse(feed_stream.content)

        feed_objs = feedparser.parse(journal.feed)

        result_items = []
        for feed in feed_objs.entries:
            item_obj = {}
            # print(feed)

            for field_name in RSSItem.model_fields.keys():
                # special case first
                if field_name == "source":
                    # We usually give a custom source name
                    item_obj[field_name] = journal.source
                    continue

                elif field_name == "uuid":
                    # use default factory function
                    continue

                elif hasattr(journal, field_name):
                    #
                    if isinstance(getattr(journal, field_name), str):
                        # if the field is a string, it means to request the corresponding field
                        item_obj[field_name] = getattr(
                            feed, getattr(journal, field_name)
                        )

                    elif isinstance(getattr(journal, field_name), DateFormat):
                        # used for date format
                        date_format: DateFormat = getattr(journal, field_name)
                        date_str = getattr(feed, date_format.datestr)
                        item_obj[field_name] = datetime.strptime(
                            date_str, date_format.format
                        )

                    elif getattr(journal, field_name) is None:
                        # if field is None, it means this field is not provided
                        pass

                    else:
                        raise NotImplementedError(
                            f"Field {field_name} is type {type(getattr(journal, field_name))}, not implemented"
                        )
                else:
                    # field not found in schema.
                    # highly likely this is a field related to LLM/scores, not included in the RSS feed
                    continue
                    # raise ValueError(f"Field {field_name} not found in RSSItem model")

            item = RSSItem.model_validate(item_obj)
            result_items.append(item)

        all_links = [item.link for item in result_items]

        if session is not None:
            # store to database, but check existing first
            existing_items = session.exec(
                select(RSSItem).where(RSSItem.link.in_(all_links))
            ).all()

            existing_links = [item.link for item in existing_items]
            new_links = []
            
            for item in result_items:
                # check duplicate
                if item.link in existing_links:
                    if update_duplicate:
                        # TODO
                        # update duplicate items
                        logger.debug(
                            f"Updating existing entries not implemented yet: {item.link}"
                        )
                        pass
                else:
                    logger.info(f"Adding new item to database: {item.link}, {item.uuid}")
                    new_links.append(item.link)
                    session.add(item)

            session.commit()

            return {"all": all_links, "new": new_links, "existing": existing_links}

        else:
            return {"all": all_links}



