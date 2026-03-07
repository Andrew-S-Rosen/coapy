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
    years_back: int | None = 4,
    filename: str | Path | None = "coauthors.csv",
) -> list[tuple[str, int, str]]:
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
    list[tuple[str, int, str]]
        List of (coauthor, most_recent_year, affiliation) tuples from the past N years.
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
    return scholarly.fill(profile, sections=sections)  # type: ignore


def _get_coauthors_from_pubs(
    papers: list[Publication],
    year_cutoff: int | None = None,
    my_name: str | None = None,
) -> list[tuple[str, int, str]]:
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
    list[tuple[str, int, str]]
        List of (coauthor, most_recent_year, affiliation) tuples.
    """

    # Filter by year
    current_year = datetime.date.today().year
    if year_cutoff:
        papers_subset = [
            paper
            for paper in papers
            if int(paper["bib"].get("pub_year", current_year)) >= year_cutoff  # type: ignore
        ]
    else:
        papers_subset = papers

    # Fetch all co-authors from publications, tracking the most recent year per author
    coauthor_years: dict[str, int] = {}
    for paper in tqdm(papers_subset):
        paper_full = scholarly.fill(paper, sections=["authors"])  # type: ignore
        pub_year = int(paper_full["bib"].get("pub_year", current_year))
        coauthors = paper_full["bib"]["author"].split(" and ")
        for coauthor in coauthors:
            if coauthor not in coauthor_years or pub_year > coauthor_years[coauthor]:
                coauthor_years[coauthor] = pub_year

    # Remove your own name
    if my_name and my_name in coauthor_years:
        del coauthor_years[my_name]

    # Clean up names and pair with most recent year and affiliation
    names = list(coauthor_years.keys())
    cleaned_names = _nsf_name_cleanup(names)
    result = [
        (cleaned, coauthor_years[orig], _get_affiliation(orig))
        for orig, cleaned in tqdm(
            zip(names, cleaned_names),
            desc="Fetching affiliations",
            total=len(names),
        )
    ]
    result.sort()

    return result


def _get_affiliation(name: str) -> str:
    """
    Search Google Scholar for an author by name and return their affiliation.

    Parameters
    ----------
    name : str
        Full name of the author as it appears on Google Scholar.

    Returns
    -------
    str
        Affiliation string from the author's Google Scholar profile, or an
        empty string if no profile is found.
    """
    try:
        author = next(scholarly.search_author(name))
        return author.get("affiliation", "")
    except StopIteration:
        return ""


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

    with Path(filename).open(mode="w", encoding="utf-8") as f:
        for coauthor, year, affiliation in co_authors:
            last, first = coauthor.split(", ", 1)
            f.write(f"{last},{first},{year},{affiliation}\n")
