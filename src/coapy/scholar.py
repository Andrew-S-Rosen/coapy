from __future__ import annotations

import datetime
import math
from pathlib import Path
from typing import TYPE_CHECKING

from scholarly import scholarly
from tqdm import tqdm

if TYPE_CHECKING:
    from scholarly.data_types import Author, Publication


def get_coauthors(
    scholar_id: str = "lHBjgLsAAAAJ",
    years_back: int | None = 4,
    filename: str | Path | None = "coauthors.csv",
) -> list[str]:
    """
    Given a Google Scholar ID, return a list of coauthors from the past N years.

    Parameters
    ----------
    scholar_id : str
        Google Scholar ID of the author. This is the string of characters
        that appears in the URL of the author's Google Scholar profile
        immediately after "user=" and before "&hl=".
    years_back : int | None
        Number of years to look back for coauthors. Set to `None` for no limit.
    filename : str | Path | None
        Path to the CSV file to write to, if any.

    Returns
    -------
    list[str]
        List of coauthors from the past N years.
    """
    today = datetime.date.today()
    year_cutoff = (today.year - years_back) if years_back else None

    profile = _get_scholar_profile(scholar_id)

    co_authors = _get_coauthors_from_pubs(
        profile["publications"], year_cutoff=year_cutoff, my_name=profile["name"]
    )
    if filename:
        _dump_to_csv(co_authors, filename)
    return co_authors


def _get_scholar_profile(scholar_id: str, sections: list[str] | None = None) -> Author:
    """
    Given a Google Scholar ID, return the full profile.

    Parameters
    ----------
    scholar_id : str
        Google Scholar ID of the author. This is the string of characters
        that appears in the URL of the author's Google Scholar profile
        immediately after "citations?user=" and before "&hl=".
    sections : list[str] | None
        Sections of the profile to return. If None, return the default
        sections selected by scholarly.

    Returns
    -------
    Author
        Full profile of the author.
    """
    if sections is None:
        sections = []
    profile = scholarly.search_author_id(scholar_id)
    return scholarly.fill(profile, sections=sections)


def _get_coauthors_from_pubs(
    papers: list[Publication],
    year_cutoff: int | None = None,
    my_name: str | None = None,
) -> dict[str, int]:
    """
    Get a de-duplicated list of co-authors from a list of publications.

    Parameters
    ----------
    papers : list[Publication]
        List of publications.
    year_cutoff : int | None
        Year before which to ignore publications. If set to `None`, all
        publications will be considered.
    my_name : str | None
        Name of the author. If set to `None`, the author will still be
        included in the list of co-authors.

    Returns
    -------
    dict[str, int]
        Dictionary of {co-author: most recent year of collaboration}.
    """

    # Set year_cutoff to infinity if not provided
    if year_cutoff is None:
        year_cutoff = math.inf

    # Filter by year
    current_year = datetime.date.today().year
    paper_subset = []
    year_subset = []
    for paper in papers:
        pub_year = int(paper["bib"].get("pub_year", current_year))
        if pub_year >= year_cutoff:
            paper_subset.append(paper)
            year_subset.append(pub_year)

    # Fetch all co-authors from publications
    all_coauthors = []
    all_years = []
    for paper, pub_year in tqdm(
        zip(paper_subset, year_subset), total=len(paper_subset)
    ):
        paper_full = scholarly.fill(paper, sections=["coauthors"])
        coauthors = paper_full["bib"]["author"].split(" and ")

        all_coauthors.extend(coauthors)
        all_years.extend([pub_year] * len(coauthors))

    # Clean up list of co-authors
    all_coauthors = _nsf_name_cleanup(all_coauthors)
    all_coauthors, all_years = zip(*sorted(zip(all_coauthors, all_years)))

    # Convert the result back to lists
    all_coauthors = list(all_coauthors)
    all_years = list(all_years)

    # De-duplicate and store most recent year
    coauthor_year_map = {}
    for coauthor, year in zip(all_coauthors, all_years):
        if coauthor in coauthor_year_map:
            coauthor_year_map[coauthor] = max(coauthor_year_map[coauthor], year)
        else:
            coauthor_year_map[coauthor] = year

    # Remove your own name
    if my_name:
        coauthor_year_map.pop(my_name, None)

    return coauthor_year_map


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
    co_authors: dict[str, int], filename: str | Path = "coauthors.csv"
) -> None:
    """
    Dump a list of coauthors to a CSV file.

    Parameters
    ----------
    co_authors : dict[str, int]
        List of coauthors with year of most recent collaboration.
    filename : str | Path
        Name of the CSV file to write to.

    Returns
    -------
    None
    """

    with Path(filename).open(mode="w", encoding="utf-8") as f:
        for coauthor, year in co_authors.items():
            f.write(f"{coauthor}, {year}\n")
