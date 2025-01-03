import os
import db
import json
from prefect import flow, task
from dotenv import load_dotenv
from prefect.client.schemas.schedules import CronSchedule
from generate_site import generate_html_jinja
import datetime
from ai import get_openai_completion

load_dotenv(".env")

Session = db.create_session()

URLS = os.getenv("URLS")
URLS = json.loads(URLS)


@task
def add_url_download(url):
    download_db = Session.add(db.Downloads(url=url, type="test"))
    Session.commit()
    return download_db


@task
def check_for_downloads():
    downloads = Session.query(db.Downloads).filter_by(status="pending").all()
    for download in downloads:
        download.download()
        Session.commit()
    return downloads


@task
def check_for_processed():
    downloads = Session.query(db.Downloads).filter_by(status="downloaded").all()
    for download in downloads:
        with download.process(Session) as f:
            ids = json.load(f)
            for _id in ids:
                url = f"https://hacker-news.firebaseio.com/v0/item/{_id}.json"
                # download_db = Session.add(db.Downloads(url=url, type="article"))
                db.get_or_create(Session, db.Downloads, url=url, type="article")
                Session.commit()
    return downloads


@task
def check_for_articles():
    downloads = (
        Session.query(db.Downloads).filter_by(type="article", status="downloaded").all()
    )
    for download in downloads:
        with download.process(Session, set_status=False) as f:
            data = json.load(f)
            article = db.get_or_create(Session, db.Article, uid=data["id"])
            article.timestamp = data.get("time", None)
            article.published_at = (
                datetime.datetime.fromtimestamp(article.timestamp)
                if article.timestamp
                else None
            )
            article.download_id = download.id
            article.title = data.get("title", None)
            Session.commit()

    return downloads


@task
def enrich_with_ai(article):

    system_prompt = f"""You are an experienced hacker news reader, expand on the short title give with a summary under 50 words."""
    prompt = f"""{article.title}"""

    message, input, output = get_openai_completion(
        prompt=prompt, system_prompt=system_prompt
    )

    openai_id = output["id"]

    input = json.dumps(input, indent=2, default=str)
    output = json.dumps(output, indent=2, default=str)

    ai_article = db.AiArticles(article_id=article.id, query=input, response=output)
    Session.add(ai_article)
    Session.commit()
    ai_article.uid = openai_id
    Session.commit()


@flow(name="download-flow")
def download_flow():
    for url in URLS:
        add_url_download(url)
    check_for_downloads()


@flow(name="process-index")
def process_index_flow():
    check_for_processed()


@flow(name="download-articles")
def download_articles_flow():
    check_for_downloads()


@flow(name="openai-enrichment")
def openai_enrichment():
    articles = (
        Session.query(db.Article)
        .outerjoin(db.AiArticles)
        .filter(db.AiArticles.article_id == None)
        .all()
    )
    for article in articles:
        enrich_with_ai(article)


@flow(name="generate-html")
def generate_html_flow():
    # create context
    articles = Session.query(db.Article).order_by(db.Article.published_at.desc())
    for i, article in enumerate(articles):
        # print(article.ai_articles[0].response_json)
        response = article.ai_articles[0].response_json
        message = response["choices"][0]["message"]["content"]
        articles[i].open_ai = message
    context = {"articles": articles}
    generate_html_jinja(context)
