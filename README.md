# An ETL AI Data Pipeline

(Almost) production ready example ETL / AI static site generator using Prefect, Jinja & SQLAlchemy

1. Download API / Parse APi Endpoint
2. Add article downloads to queue
3. Add to OpenAI Queue for summary
4. Collect all data
5. Generate site

Quick start

```sh
# (optional) create virtual env
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# create .env
cp .env.example .env # make any modifications to .env

# (optional) runs tests
python3 ./tests.py

# migrate downloads db
alembic upgrade head

python3 ./main.py

```

# Selected Dependencies

```sh
prefect
sqlalchemy
alembic
```

# Future Work

- Dockerize w/ postgres
- Async flows
-

# Appendix

```sh

alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
echo .dump | sqlite3 downloads.db

```
