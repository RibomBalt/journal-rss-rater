from typing import Optional, Annotated
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select
from pydantic import BaseModel, ConfigDict, field_validator
import uuid

class AllowExtraModel(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )

# RSS
# ==========================
class RSSItem(SQLModel, table=True):
    __tablename__ = "rss_items"

    # use UUID as primary key
    uuid: str = Field(
        default_factory=lambda: uuid.uuid4().hex, primary_key=True
    )  # RSS项ID

    title: str  # 标题
    link: str  # 链接
    summary: str  # 摘要
    source: str  # 来源
    authors: Optional[str] = ""  # 作者
    affiliation: Optional[str] = ""  # 作者单位
    published: datetime = Field(index=True)  # 发布时间

    llm_comments: Optional[str] = Field(
        default=""
    )  # LLM评价
    llm_score: Optional[float] = Field(
        default=None, index=True
    )  # LLM相关性评分
    relevance_score: Optional[float] = Field(
        default=None, index=True
    )  # 最终相关性评分


class DateFormat(BaseModel):
    datestr: str
    format: str


class RSS_Journal(AllowExtraModel):
    """
    this is used to parse rss.yml to get correspondence with sqlmodels
    """

    feed: str
    source: str

    title: Optional[str] = Field(default="title")
    link: Optional[str] = Field(default="link")
    summary: Optional[str] = Field(default="summary")
    authors: Optional[str] = Field(default="authors")
    affiliation: Optional[str] = Field(default="affiliation")
    published: DateFormat = Field(default="published")


