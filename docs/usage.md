# Usage

## Pre-Requisites

Fetch your ORCID, which is a 16-digit identifier in the format `0000-0000-0000-0000`. You can find or register for one at [orcid.org](https://orcid.org). Make sure your publications are up to date in your ORCID profile, as coapy uses your ORCID record as the source of truth for which papers belong to you.

## Examples

If generating an NSF COA or DOE collaborators report, all you need to do is the following. By default, the code will write out an Excel file `"coauthors.xlsx"` to the current working directory with four columns: last name, first name, most recent collaboration year, and institutional affiliation(s). By default, it will fetch data 4 years back.

```python
from coapy.scholar import get_coauthors

orcid = "0000-0002-0141-7006"
my_coauthors = get_coauthors(orcid=orcid)
```

If you need to get co-authors for a different number of years back in time, this can be modified as follows:

```python
from coapy.scholar import get_coauthors

orcid = "0000-0002-0141-7006"
my_coauthors = get_coauthors(orcid=orcid, years_back=5)
```

## Notes

- The institutional affiliation data is pulled from [OpenAlex](https://openalex.org/). OpenAlex will often include more institutional affiliations than are needed. For instance, if the person switched institutions, multiple may be listed. These should be spot-checked if you really care about having the institutional affiliations perfect.
