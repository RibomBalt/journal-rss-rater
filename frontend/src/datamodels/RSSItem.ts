class RSSItem {
  // UUID 作为主键
  uuid: string; // RSS项ID

  // 必填字段
  title: string; // 标题
  link: string; // 链接
  summary: string; // 摘要
  source: string; // 来源
  published: Date; // 发布时间 (注意：Pydantic 的 datetime 类型在 TypeScript 中使用 string)

  // 可选字段，默认为空字符串
  authors: string | null; // 作者
  affiliation: string | null; // 作者单位

  // 可选字段，默认为空字符串或 null
  llm_comments: string | null; // LLM评价
  llm_score: number | null; // LLM相关性评分
  relevance_score: number | null; // 最终相关性评分

  constructor({
    uuid,
    title,
    link,
    summary,
    source,
    published,
    authors = null,
    affiliation = null,
    llm_comments = null,
    llm_score = null,
    relevance_score = null,
  }: Omit<RSSItem, 'published'> & { published: string }) {
    this.uuid = uuid;
    this.title = title;
    this.link = link;
    this.summary = summary;
    this.source = source;
    this.published = new Date(published);
    this.authors = authors;
    this.affiliation = affiliation;
    this.llm_comments = llm_comments;
    this.llm_score = llm_score;
    this.relevance_score = relevance_score;
  }

}

export default RSSItem;