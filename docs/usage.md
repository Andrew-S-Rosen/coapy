# Usage

## Pre-Requisites

Fetch your ORCID, which is a 16-digit identifier in the format `0000-0000-0000-0000`. You can find or register for one at [orcid.org](https://orcid.org). Make sure your publications are up to date in your ORCID profile, as coapy uses your ORCID record as the source of truth for which papers belong to you.

## Examples

If generating an NSF COA report, all you need to do is the following. By default, the code will write out a CSV file `"coauthors.csv"` to the current working directory with four columns: last name, first name, most recent collaboration year, and institutional affiliation(s).

```python
from coapy.scholar import get_coauthors

orcid = "0000-0002-2365-7464"  # ORCID
my_coauthors = get_coauthors(orcid=orcid)
print(my_coauthors)
```

If for any reason you need to get >4 years of data, this can be modified as follows:

```python
from coapy.scholar import get_coauthors

orcid = "0000-0002-2365-7464"  # ORCID
my_coauthors = get_coauthors(orcid=orcid, years_back=5)
print(my_coauthors)
```

To fetch all coauthors with no year limit:

```python
from coapy.scholar import get_coauthors

orcid = "0000-0002-2365-7464"  # ORCID
my_coauthors = get_coauthors(orcid=orcid, years_back=None)
print(my_coauthors)
```
