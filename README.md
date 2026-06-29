# coapy

![tests](https://github.com/quantum-accelerators/coapy/actions/workflows/tests.yaml/badge.svg)

A Python package for generating a list of collaborators suitable for an [NSF Collaborators and Other Affiliations (COA) document](https://www.nsf.gov/bfa/dias/policy/coa/coa_template.xlsx) or [DOE Collaborators form](https://science.osti.gov/-/media/grants/excel/Collaborator_Template.xlsx).

<p align="center">
  📖 <a href="https://andrew-s-rosen.github.io/coapy/"><b><i>Check out the documentation!</i></b></a> 📖
</p>

# Usage

```python
from coapy.scholar import get_coauthors

orcid = "0000-0002-0141-7006"
my_coauthors = get_coauthors(orcid=orcid) # writes out to `coauthors.xlsx`
```
