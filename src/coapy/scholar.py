from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from scholarly import scholarly
from tqdm import tqdm

if TYPE_CHECKING:
    from scholarly.data_types import Author, Publication


def get_coauthors(
    scholar_id: str = "lHBjgLsAAAAJ",
    years_back: int | None = 2,
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
) -> list[str]:
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
    list[str]
        List of co-authors.
    """

    # Filter by year
    current_year = datetime.date.today().year
    if year_cutoff:
        papers_subset = [
            paper
            for paper in papers
            if int(paper["bib"].get("pub_year", current_year)) >= year_cutoff
        ]
    else:
        papers_subset = papers

    # Fetch all co-authors from publications
    all_coauthors = []
    for paper in tqdm(papers_subset):
        paper_full = scholarly.fill(paper, sections=["authors"])
        coauthors = paper_full["bib"]["author"].split(" and ")

        all_coauthors.extend(coauthors)

    # De-duplicate list of co-authors and remove your own name
    all_coauthors = list(set(all_coauthors))
    if my_name and my_name in all_coauthors:
        all_coauthors.remove(my_name)

    # Clean up list of co-authors
    all_coauthors = _nsf_name_cleanup(all_coauthors)
    all_coauthors.sort()

    return all_coauthors


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


def _dump_to_csv(co_authors: list[str], filename: str | Path = "coauthors.csv") -> None:
    """
    Dump a list of coauthors to a CSV file.

    Parameters
    ----------
    co_authors : list[str]
        List of coauthors.
    filename : str | Path
        Name of the CSV file to write to.

    Returns
    -------
    None
    """

    with Path(filename).open(mode="w", encoding="utf-8") as f:
        for coauthor in co_authors:
            f.write(f"{coauthor}\n")
