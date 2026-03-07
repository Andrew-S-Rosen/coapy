# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Replaced `scholarly` (unmaintained) with direct API calls to ORCID and OpenAlex
- Paper list is now sourced from the user's ORCID profile (user-curated) rather than OpenAlex author disambiguation
- Co-author details (names, institutions, publication year) are fetched from OpenAlex by DOI
- `scholar_id` parameter replaced by `orcid` (e.g., `"0000-0002-2365-7464"`)
- CSV output now includes four columns: last name, first name, most recent collaboration year, affiliation(s)
- Multiple institutional affiliations for a co-author are separated by ` / `
- CSV is written with a UTF-8 BOM for correct display in Excel

## [0.0.2]

### Added

- Added a progress bar
- A CSV file will be written out by default

### Fixed

- Fixed `years_back` parsing

## [0.0.1]

### Added

- The initial release!
