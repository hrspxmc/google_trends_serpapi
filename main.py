import pandas as pd
import json
import os.path

from tqdm import tqdm
from lib.process_data import *

with open("config.json") as f:
    config = json.load(f)

for kwd_list in (pbar:=tqdm(config["keywords"], position=0, leave=True)):

    pbar.set_postfix_str(kwd_list)

    kwd_related_queries = pd.concat(
        [
            extract_related_queries(ii, config["URL"], config["base_params"])
            for ii in kwd_list
        ]
    ).reset_index(drop=True)

    related_keywords = construct_new_keywords(kwd_related_queries, kwd_list, 4)
    related_keywords = [ii for ii in related_keywords if len(ii) > 1]
    interest_over_time = pd.concat(
        [
            extract_interest_over_time(ii, config['URL'], config["base_params"])
            for ii in kwd_list + related_keywords
        ]
    )

    if os.path.isfile(config["interest_over_time_file"]):
        interest_over_time.to_csv(config["interest_over_time_file"], index=False)
    else:
        interest_over_time.to_csv(
            config["interest_over_time_file"], mode="a", header=False, index=False
        )

    if os.path.isfile(config["releated_keywords_file"]):
        kwd_related_queries.to_csv(config["releated_keywords_file"], index=False)
    else:
        kwd_related_queries.to_csv(
            config["releated_keywords_file"], mode="a", header=False, index=False
        )
