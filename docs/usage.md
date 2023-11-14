# Usage

## Pre-Requisites

Fetch your Google Scholar ID, which is the string of letters and numbers in the URL of your Google Scholar profile page between `user=` and `&hl=`.

## Example

```python
from coapy.scholar import get_coauthors

scholar_id = "lHBjgLsAAAAJ" # Google Scholar ID
my_coauthors = get_coauthors(scholar_id=scholar_id)
print(my_coauthors)
```
