# Methods, provenance and limitations

## Purpose and fixture provenance

This is a bounded software example from MatrixBioservices, whose initial product focus is scientist-led CHO cell line development and clone screening decision support. The example does not implement the scientific product or provide screening, upload or inference services.

All fixture identifiers, sources, units, values, exclusions and timestamps are invented `TEST_FIXTURE` software records. They are not customer records, measurements or a simulated CHO experiment. The values 1 and 9 are arbitrary and have no biological meaning, empirical threshold or clone-ranking interpretation. No third-party implementation code or dataset is bundled; Python is an external prerequisite.

## Artificial-record checks

`qc_example.py` requires a nonempty list of record objects. It checks the fixture label, unique nonempty identifiers, nonempty source declarations, the exact test unit, finite numeric values and explicit Boolean eligibility. Booleans are not accepted as numeric values. An excluded record requires an exclusion reason.

Timestamps must include a timezone and satisfy `observed_at <= available_at <= cutoff`. This checks declared availability at a decision cutoff; it does not establish that a source or timestamp is truthful. The CLI also rejects duplicate JSON keys and nonfinite JSON constants.

The output retains the registry count, lists eligible identifiers and reports findings. A finding makes the overall status `FAIL`, even if another valid row contributes an eligible identifier. Consumers must check the overall status. Exit status 0 means the software checks passed; exit status 2 means input or checks did not pass. `scientific_interpretation` is `NONE_TEST_FIXTURE` and `release_authorised` is always `false`. Neither eligibility nor exclusion is a biological retain/drop recommendation.

## Separate evidence-declaration helper

`mandatory_evidence.py` contains selected generic validation functions for test-run and preservation declarations. Findings are reported through a caller-supplied callback. It has no standalone CLI and is not called by the artificial-record CLI.

The `test-run-p2-1` declaration requires exactly these count keys: `run`, `passed`, `failures`, `errors`, `skipped`, `expected_failures` and `unexpected_successes`. Counts must be nonnegative integers, not booleans; `run` must be positive and equal the sum of the other categories. This example producer's acceptance rule requires every category except `run` and `passed` to be zero, including skipped tests and expected failures. That is not a universal `unittest` policy.

`started_at` and `finished_at` must parse with Python's `datetime.fromisoformat`, include a timezone and satisfy start <= finish. Terminal `Z` is normalized to `+00:00`. Equal instants and offset-equivalent times are allowed. There is no trusted clock or execution-window input, so freshness and future-date rejection are outside the helper's contract. Supported ISO forms can differ between Python versions; the tests cover the documented forms.

Other checks include required fields, hash-string formats, a zero return code, an unchanged-files declaration and a nonempty declared tested-file map. Preservation declarations check selected status fields, equal positive before/after counts, empty change/mismatch lists and explicit inherited flags. These checks validate declarations, not their underlying evidence.

The helper does not open or hash referenced files or logs, authenticate producers, verify signatures or reproduce execution. Counts, dates and claimed hashes can still be fabricated. Passing the helper does not establish completeness, actual preservation or execution assurance.

## Reproducibility and validation limits

The README commands reproduce this small software example using the included fixture and 24 tests. The tests exercise record validation, CLI behavior and selected evidence-contract rules. They do not assess a scientific model, real longitudinal CLD data, customer outcomes, email delivery or a production service.

The current MatrixBioservices research system is an integrated synthetic-data prototype. Real longitudinal CLD and customer validation have not been completed. No predictive accuracy, clone-selection benefit, cost saving, biological performance, GxP/GMP qualification or regulatory suitability is demonstrated here. Scientists remain the final scientific decision-makers. Invalid or insufficient evidence is not a biological failure label.

Scientific engines, training and inference pipelines, model weights, proprietary unpublished methods, private experimental data and internal operational records are not included. Software reproducibility here is not reproduction of the private research system or scientific validation of it.

## Rights and safe use

The included code, documentation and artificial fixture are distributed under the repository's [MIT License](../LICENSE), with copyright attributed to MatrixBioservices. The grant covers the included files; it does not grant access or rights to excluded proprietary assets. The license provides no warranty.

Do not place credentials, personal information, customer data or confidential experimental records in public issues. Use an appropriate private, permissioned process for any future customer analysis.
