from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from scholarly import scholarly

if TYPE_CHECKING:
    from scholarly.data_types import Author, Publication


def get_coauthors(id: str = "lHBjgLsAAAAJ", years: int | None = 2) -> list[str]:
    """
    Given a Google Scholar ID, return a list of coauthors from the past N years.

    Parameters
    ----------
    id : str
        Google Scholar ID of the author. This is the string of characters
        that appears in the URL of the author's Google Scholar profile
        immediately after "citations?user=" and before "&hl=".
    years : int
        Number of years to look back for coauthors. Set to `None` for no limit.

    Returns
    -------
    list[str]
        List of coauthors from the past N years.
    """
    today = datetime.date.today()
    year_cutoff = (today.year - years) if years else None

    profile = _get_scholar_profile(id)

    return _get_coauthors_from_pubs(
        profile["publications"], year_cutoff=year_cutoff, my_name=profile["name"]
    )


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
    year_cutoff : int
        Year before which to ignore publications. If set to `None`, all
        publications will be considered.
    my_name : str
        Name of the author. If set to `None`, the author will still be
        included in the list of co-authors.

    Returns
    -------
    list[str]
        List of co-authors.
    """

    # Fetch all co-authors from publications
    all_coauthors = []
    for paper in papers:
        paper_full = scholarly.fill(paper, sections=["authors"])
        coauthors = paper_full["bib"]["author"].split(" and ")

        if year_cutoff and paper_full["bib"]["pub_year"] >= year_cutoff:
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
    for i, coauthor in enumerate(coauthors):
        name_parts = coauthor.split(" ")
        reordered_name = f"{name_parts[-1]}, {' '.join(name_parts[:-1])}"
        cleaned_coauthors[i] = reordered_name
    return cleaned_coauthors


def _get_scholar_profile(id: str, sections: list[str] = None) -> Author:
    """
    Given a Google Scholar ID, return the full profile.

    Parameters
    ----------
    id : str
        Google Scholar ID of the author. This is the string of characters
        that appears in the URL of the author's Google Scholar profile
        immediately after "citations?user=" and before "&hl=".
    sections : list[str]
        Sections of the profile to return. If None, return the default
        sections selected by scholarly.

    Returns
    -------
    Author
        Full profile of the author.
    """
    if sections is None:
        sections = []
    profile = scholarly.search_author_id(id)
    return scholarly.fill(profile, sections=sections)
