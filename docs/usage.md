# Usage

## Pre-Requisites

Fetch your Google Scholar ID, which is the string of letters and numbers in the URL of your Google Scholar profile page between `user=` and `&hl=`.

## Examples

If generating an NSF COA report, all you need to do is the following:

```python
from coapy.scholar import get_coauthors

scholar_id = "lHBjgLsAAAAJ" # Google Scholar ID
my_coauthors = get_coauthors(scholar_id=scholar_id)
print(my_coauthors)
```

If for any reason you need to get >2 years of data, this can be modified as follows:

```python
from coapy.scholar import get_coauthors

scholar_id = "lHBjgLsAAAAJ" # Google Scholar ID
my_coauthors = get_coauthors(scholar_id=scholar_id, years_back=4)
print(my_coauthors)
```
