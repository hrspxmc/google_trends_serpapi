import requests
import pandas as pd

from datetime import datetime


def mdy_to_ymd(d):
    return datetime.strptime(d, "%b %d, %Y").strftime("%Y-%m-%d")


def df_from_query(timeline_data):
    df = pd.DataFrame.from_dict(timeline_data["values"])
    df["date"] = mdy_to_ymd(timeline_data["date"])
    return df


def extract_related_queries(keyword, url, base_params, top_n=4):
    params = {
        "q": keyword,
        "data_type": "RELATED_QUERIES",
    }

    response = requests.get(url, params=base_params | params)
    if "error" not in response.json():
        pd_related = pd.DataFrame.from_dict(response.json()["related_queries"]["top"])
        pd_related["base_keyword"] = keyword
        pd_related["query_date"] = datetime.today().strftime("%Y-%m-%d")
        pd_related["reduced_query"] = [
            ii.replace(keyword, "").strip() for ii in pd_related["query"]
        ]
    else:
        pd_related = pd.DataFrame()

    return pd_related


def extract_interest_over_time(keywords, url, base_params):
    params = {"q": ", ".join(keywords), "data_type": "TIMESERIES"}

    response = requests.get(url, params=base_params | params)

    if "error" not in response.json():
        pd_res = pd.concat(
            [
                df_from_query(ii)
                for ii in response.json()["interest_over_time"]["timeline_data"]
            ]
        ).reset_index(drop=True)
        pd_res["keywords"] = ", ".join(keywords)
        pd_res["query_date"] = datetime.today().strftime("%Y-%m-%d")
    else:
        pd_res = pd.DataFrame()

    return pd_res


def construct_new_keywords(kwd_related_queries, keywords, top_n=4):
    related_keywords = []
    for kwd in keywords:
        selected_keywords = list(
            kwd_related_queries.query('base_keyword == "{}"'.format(kwd)).head(top_n)[
                "query"
            ]
        )
        related_keywords.append([kwd] + selected_keywords)
    return related_keywords
