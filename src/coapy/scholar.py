from __future__ import annotations

import csv
import datetime
import json
from pathlib import Path

import requests
from tqdm import tqdm

OPENALEX_API = "https://api.openalex.org"
ORCID_API = "https://pub.orcid.org/v3.0"


def get_coauthors(
    orcid: str,
    years_back: int | None = 4,
    filename: str | Path | None = "coauthors.csv",
) -> list[tuple[str, int, str]]:
    """
    Given an ORCID, return a list of coauthors from the past N years.

    The paper list is sourced from the author's ORCID profile (user-curated),
    and co-author details are fetched from OpenAlex by DOI.

    Parameters
    ----------
    orcid : str
        ORCID of the author (e.g., "0000-0002-2365-7464"). Find yours at
        https://orcid.org.
    years_back : int | None
        Number of years to look back for coauthors. Set to `None` for no limit.
    filename : str | Path | None
        Path to the CSV file to write to, if any.

    Returns
    -------
    list[tuple[str, int, str]]
        List of (coauthor, most_recent_year, affiliation) tuples from the past N years.
    """
    today = datetime.date.today()
    year_cutoff = (today.year - years_back) if years_back else None

    openalex_id, my_name = _resolve_orcid(orcid)
    orcid_papers = _fetch_orcid_works(orcid, year_cutoff=year_cutoff)
    works = _fetch_works_from_openalex(orcid_papers)
    co_authors = _get_coauthors_from_works(
        works, my_openalex_id=openalex_id, my_name=my_name
    )

    if filename:
        _dump_to_csv(co_authors, filename)
    return co_authors


def _resolve_orcid(orcid: str) -> tuple[str, str]:
    """
    Resolve an ORCID to an OpenAlex author ID and display name.

    Parameters
    ----------
    orcid : str
        ORCID of the author (e.g., "0000-0002-2365-7464").

    Returns
    -------
    tuple[str, str]
        The OpenAlex author ID (short form) and display name.
    """
    response = requests.get(
        f"{OPENALEX_API}/authors/https://orcid.org/{orcid}",
        timeout=30,
    )
    response.raise_for_status()
    author = json.loads(response.content)
    return author["id"].split("/")[-1], author["display_name"]


def _fetch_orcid_works(
    orcid: str, year_cutoff: int | None = None
) -> list[dict]:
    """
    Fetch the author's papers from their ORCID profile.

    Only papers with a DOI are returned, as those are needed for OpenAlex lookup.

    Parameters
    ----------
    orcid : str
        ORCID of the author.
    year_cutoff : int | None
        Earliest publication year to include. Papers with no year are always included.

    Returns
    -------
    list[dict]
        List of {"doi": str, "year": int | None} dicts.
    """
    response = requests.get(
        f"{ORCID_API}/{orcid}/works",
        headers={"Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    data = json.loads(response.content)

    papers = []
    for group in data.get("group", []):
        summaries = group.get("work-summary", [])
        if not summaries:
            continue
        summary = summaries[0]

        # Get publication year
        pub_date = summary.get("publication-date") or {}
        year_str = (pub_date.get("year") or {}).get("value")
        year = int(year_str) if year_str else None

        if year_cutoff and year and year < year_cutoff:
            continue

        # Find DOI
        doi = None
        for ext_id in (summary.get("external-ids") or {}).get("external-id", []):
            if ext_id.get("external-id-type") == "doi":
                doi = ext_id.get("external-id-value", "").strip().lower()
                break

        if doi:
            papers.append({"doi": doi, "year": year})

    return papers


def _fetch_works_from_openalex(papers: list[dict]) -> list[dict]:
    """
    Look up each paper in OpenAlex by DOI to retrieve authorship and institution data.

    Papers not found in OpenAlex are silently skipped.

    Parameters
    ----------
    papers : list[dict]
        List of {"doi": str, "year": int | None} dicts from ORCID.

    Returns
    -------
    list[dict]
        List of OpenAlex work records.
    """
    works = []
    for paper in tqdm(papers, desc="Fetching paper details"):
        response = requests.get(
            f"{OPENALEX_API}/works/https://doi.org/{paper['doi']}",
            timeout=30,
        )
        if response.status_code == 404:
            continue
        response.raise_for_status()
        work = json.loads(response.content)
        # Fall back to ORCID year if OpenAlex doesn't have one
        if not work.get("publication_year") and paper.get("year"):
            work["publication_year"] = paper["year"]
        works.append(work)
    return works


def _get_coauthors_from_works(
    works: list[dict],
    my_openalex_id: str,
    my_name: str | None = None,
) -> list[tuple[str, int, str]]:
    """
    Get a de-duplicated list of co-authors from a list of works.

    For each co-author, tracks the most recent year of collaboration and their
    institutional affiliation from that paper.

    Parameters
    ----------
    works : list[dict]
        List of work records from the OpenAlex API.
    my_openalex_id : str
        OpenAlex author ID of the user, used to exclude them from results.
    my_name : str | None
        Display name of the user, used as a fallback for self-exclusion.

    Returns
    -------
    list[tuple[str, int, str]]
        List of (coauthor, most_recent_year, affiliation) tuples.
    """
    current_year = datetime.date.today().year
    my_id = my_openalex_id.split("/")[-1]

    # author_id -> (display_name, most_recent_year, affiliation_at_that_year)
    coauthor_data: dict[str, tuple[str, int, str]] = {}

    for work in works:
        pub_year = work.get("publication_year") or current_year
        for authorship in work.get("authorships") or []:
            author = authorship.get("author") or {}
            author_id = (author.get("id") or "").split("/")[-1]
            author_name = author.get("display_name", "")

            if author_id == my_id:
                continue
            if my_name and author_name == my_name:
                continue

            institutions = authorship.get("institutions") or []
            affiliation = " / ".join(
                inst["display_name"] for inst in institutions if inst.get("display_name")
            )

            if author_id not in coauthor_data or pub_year > coauthor_data[author_id][1]:
                coauthor_data[author_id] = (author_name, pub_year, affiliation)

    # Clean up names and build result
    entries = list(coauthor_data.values())
    cleaned_names = _nsf_name_cleanup([name for name, _, _ in entries])
    result = [
        (cleaned, year, affiliation)
        for cleaned, (_, year, affiliation) in zip(cleaned_names, entries)
    ]
    result.sort()

    return result


def _nsf_name_cleanup(coauthors: list[str]) -> list[str]:
    """
    Clean up names to be in the NSF format of "Lastname, Firstname Middle".

    Parameters
    ----------
    coauthors : list[str]
        List of co-authors.

    Returns
    -------
    list[str]
        List of co-authors with names cleaned up.
    """
    cleaned_coauthors = []
    for coauthor in coauthors:
        name_parts = coauthor.split(" ")
        reordered_name = f"{name_parts[-1]}, {' '.join(name_parts[:-1])}"
        cleaned_coauthors.append(reordered_name)
    return cleaned_coauthors


def _dump_to_csv(
    co_authors: list[tuple[str, int, str]], filename: str | Path = "coauthors.csv"
) -> None:
    """
    Dump a list of coauthors, their most recent collaboration year, and their
    affiliation to a CSV file.

    Parameters
    ----------
    co_authors : list[tuple[str, int, str]]
        List of (coauthor, most_recent_year, affiliation) tuples.
    filename : str | Path
        Name of the CSV file to write to.

    Returns
    -------
    None
    """
    with Path(filename).open(mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for coauthor, year, affiliation in co_authors:
            last, first = coauthor.split(", ", 1)
            writer.writerow([last, first, year, affiliation])
