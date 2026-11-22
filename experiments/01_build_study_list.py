"""Step 1: build the list of CT studies used in the experiments.

--> Reads only the public IDC index. No images are downloaded.
Output: data/study_list.csv
"""
import os

import pandas as pd
from idc_index import IDCClient

SEED = 0
MIN_SLICES = 30      # drops scouts and localizers
MAX_SIZE_MB = 150    # keeps downloads small

# collection id -> maximum number of studies taken
CALIBRATION = {"eay131": 600}
TEST = {"acrin_nsclc_fdg_pet": 250, "lung_pet_ct_dx": 250, "cmb_lca": 250}

# raw BodyPartExamined value -> label group
BODY_PART_MAP = {
    "CHEST": "chest", "LUNG": "chest", "THORAX": "chest",
    "ABDOMEN": "abdomen", "LIVER": "abdomen", "KIDNEY": "abdomen",
    "COLON": "abdomen", "PANCREAS": "abdomen", "SPLEEN": "abdomen",
    "HEAD": "head_neck", "BRAIN": "head_neck", "NECK": "head_neck",
    "HEADNECK": "head_neck",
    "PELVIS": "pelvis", "BLADDER": "pelvis", "PROSTATE": "pelvis",
    "UTERUS": "pelvis", "OVARY": "pelvis",
    "CHESTABDPELVIS": "multi", "CHESTABDOMEN": "multi",
    "ABDOMENPELVIS": "multi",
}


def map_body_part(raw) -> str:
    if raw is None or pd.isna(raw) or str(raw).strip() == "":
        return "missing"
    return BODY_PART_MAP.get(str(raw).strip().upper(), "other")


def load_series(client: IDCClient, collections: list) -> pd.DataFrame:
    names = ", ".join(f"'{c}'" for c in collections)
    query = f"""
        SELECT collection_id, StudyInstanceUID, SeriesInstanceUID,
               BodyPartExamined, instanceCount, series_size_MB,
               Manufacturer, ManufacturerModelName
        FROM index
        WHERE Modality = 'CT'
          AND collection_id IN ({names})
          AND license_short_name LIKE 'CC BY%'
          AND license_short_name NOT LIKE '%NC%'
    """
    return client.sql_query(query)


def pick_one_series_per_study(series: pd.DataFrame) -> pd.DataFrame:
    keep = series[
        (series["instanceCount"] >= MIN_SLICES)
        & (series["series_size_MB"] <= MAX_SIZE_MB)
    ]
    # for each study, keep the series with the most slices
    best = keep.groupby("StudyInstanceUID")["instanceCount"].idxmax()
    return keep.loc[best]


def main() -> None:
    client = IDCClient()
    roles = {**{c: "calibration" for c in CALIBRATION},
             **{c: "test" for c in TEST}}
    caps = {**CALIBRATION, **TEST}

    series = load_series(client, list(roles))
    studies = pick_one_series_per_study(series)

    parts = []
    for collection, cap in caps.items():
        rows = studies[studies["collection_id"] == collection]
        if len(rows) > cap:
            rows = rows.sample(n=cap, random_state=SEED)
        parts.append(rows)
    result = pd.concat(parts, ignore_index=True)

    result["role"] = result["collection_id"].map(roles)
    result["tag_raw"] = result["BodyPartExamined"]
    result["tag_group"] = result["BodyPartExamined"].apply(map_body_part)

    os.makedirs("data", exist_ok=True)
    result.to_csv("data/study_list.csv", index=False)

    print(f"Wrote {len(result)} studies to data/study_list.csv\n")
    summary = result.groupby(["role", "collection_id", "tag_group"]).size()
    print(summary.to_string())


if __name__ == "__main__":
    main()
