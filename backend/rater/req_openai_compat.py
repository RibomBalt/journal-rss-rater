# from openai import OpenAI
import httpx
from ..models import RSSItem, AllowExtraModel
from ..config import AppSettings, LLM_Config, get_config
from sqlmodel import Session, select
from pydantic import BaseModel, ValidationError
from ..logger import custom_logger

config = get_config()
logger = custom_logger(__name__, debug=config.DEBUG)

class LLMResponse(BaseModel):
    comment: str
    score: float | None

class SiliconflowMessageScheme(AllowExtraModel):
    role: str
    content: str

class SiliconflowChoiceScheme(AllowExtraModel):
    message: SiliconflowMessageScheme
    finish_reason: str

class SiliconflowUsageScheme(AllowExtraModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class SiliconflowResponseScheme(AllowExtraModel):
    id: str
    choices: list[SiliconflowChoiceScheme]
    model: str
    object: str
    usage: SiliconflowUsageScheme


def generate_prompt(paper: RSSItem, llm_config: LLM_Config):
    """
    Generate the prompt for OpenAI API
    there are already curly braces in the prompt, we only need to fill in the blanks
    """
    prompt_template = llm_config.prompt
    prompt = prompt_template.format(**paper.model_dump())
    return prompt


def request_llm_response(prompt: str, llm_config: LLM_Config):
    """
    Request the LLM response based on httpx client
    """
    url = llm_config.base_url + "/chat/completions"
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    payload = dict(model=llm_config.model_name, messages=messages, **llm_config.model_args)
    
    headers = {
        "Authorization": f"Bearer {llm_config.api_key}",
        "Content-Type": "application/json"
    }

    resp = httpx.request(
        "POST",
        url,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if resp.status_code != 200:
        logger.warning(f"OpenAI API request failed: {resp.status_code}, {resp.text}")
        raise httpx.HTTPStatusError(f"OpenAI API request failed: {resp.status_code}, {resp.text}")

    # TODO validate 
    resp_json = resp.json()
    resp_obj = SiliconflowResponseScheme.model_validate(resp_json)

    return resp_obj


def get_openai_response(paper: RSSItem, config: AppSettings):
    """
    Get the response from OpenAI API
    TODO try-except
    """
    llm_config = config.LLM_API
    prompt = generate_prompt(paper, llm_config)

    # client = OpenAI(api_key=llm_config.api_key, base_url=llm_config.base_url)
    # resp_raw: str = client.chat.completions.create(
    #     model=llm_config.model_name,
    #     messages=[{"role": "user", "content": prompt}],
    #     **llm_config.model_args,
    # )
    resp_raw = request_llm_response(prompt, llm_config)
    logger.debug(f"OpenAI response: {resp_raw}")
    resp_msg = resp_raw.choices[0].message.content

    try:
        resp = LLMResponse.model_validate_json(resp_msg)
    except ValidationError as err:
        logger.warning(f"Validation error: {err}, response: {resp_msg}")

        return {"comment": resp_msg, "score": None}

    return resp


def rate_papers(papers: list[RSSItem], config: AppSettings, rerate: bool = False, session: Session = None):
    """ """
    rated_papers = []
    for ipaper, paper in enumerate(papers):
        if not rerate and paper.llm_score is not None:
            # This paper is already rated
            logger.debug(f"Paper #{ipaper}: {paper.link} already rated, skipping")
            continue

        logger.debug(f"Rating paper #{ipaper}: {paper.link}")
        resp = get_openai_response(paper, config)
        logger.debug(f"Rating Response: {resp}")
        paper.llm_comments = resp.comment
        paper.llm_score = resp.score
        rated_papers.append(paper)

    if session is not None:
        session.add_all(rated_papers)
        session.commit()

    return papers


def rate_all_db(session: Session, config: AppSettings, rerate: bool = False, specify_paper_link: str = None):
    """
    Rate all papers in the database
    """
    if specify_paper_link is not None:
        papers = session.exec(select(RSSItem).where(RSSItem.link == specify_paper_link)).all()
        if not papers:
            logger.warning(f"Paper {specify_paper_link} not found in database")
            return {}
    else:
        if rerate:
            papers = session.exec(select(RSSItem)).all()
        else:
            papers = session.exec(select(RSSItem).where(RSSItem.llm_score.is_(None))).all()

    papers = rate_papers(papers, config, rerate=rerate, session=session)
    return {paper.link: {"comment": paper.llm_comments, "score": paper.llm_score} for paper in papers}