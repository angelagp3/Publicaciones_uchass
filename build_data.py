import csv, json, sys, requests, os

MAILTO = "angelagp@ugr.es"          # cámbialo por tu correo real
CSV = "Publicaciones_OpenAlex_UCHASS.csv"

# Lee los IDs de OpenAlex (separador de columnas ";" y de IDs "|").
# Los miembros sin openalex_id quedan fuera automáticamente.
ids = []
with open(CSV, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f, delimiter=";"):
        ids += [i.strip() for i in r["openalex_id"].split("|") if i.strip()]
ids = list(dict.fromkeys(ids))
print(len(ids), "IDs de autor")

works = {}
for k in range(0, len(ids), 50):
    cursor = "*"
    while cursor:
        resp = requests.get("https://api.openalex.org/works", params={
            "filter": "authorships.author.id:" + "|".join(ids[k:k + 50]),
            "select": "id,title,publication_year,type,doi,open_access",
            "per-page": 100,
            "cursor": cursor,
            "mailto": MAILTO,
            "api_key": os.environ["OPENALEX_API_KEY"],
        }, timeout=60)
        resp.raise_for_status()
        r = resp.json()
        for w in r["results"]:
            works[w["id"]] = {
                "id": w["id"], "title": w["title"], "year": w["publication_year"],
                "type": w["type"], "doi": w["doi"],
                "oa": bool((w.get("open_access") or {}).get("is_oa")),
            }
        cursor = r["meta"].get("next_cursor")

if not works:
    sys.exit("No se obtuvo ninguna publicación; no se sobrescribe data.json")

json.dump(list(works.values()), open("data.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(works), "publicaciones únicas")
