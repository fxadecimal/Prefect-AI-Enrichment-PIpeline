#!/usr/bin/env python

from flows import (
    download_flow,
    process_index_flow,
    download_articles_flow,
    generate_html_flow,
    check_for_articles,
    openai_enrichment,
)

if __name__ == "__main__":
    # download_flow()
    # print(process_index_flow())
    # download_articles_flow()
    # check_for_articles()
    # openai_enrichment()
    generate_html_flow()

    # download_flow.serve(
    #     name="cron-download-flow",
    #     schedules=[CronSchedule(cron="* * * * *", timezone="UTC")],
    # )
