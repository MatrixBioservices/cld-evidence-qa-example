# CLD Evidence QA Example

**MatrixBioservices — Scientific Intelligence for Biologics Manufacturing.**

MatrixBioservices develops AI decision support for biologics manufacturing, starting with scientist-led **CHO Cell Line Development and Clone Screening Decision Intelligence**. Our current research system is an integrated synthetic-data prototype. Real longitudinal CLD and customer validation have not been completed; scientists remain the final scientific decision-makers.

This repository is a small, reproducible Python example for scientists and developers who want to inspect how software can check evidence records. It uses two invented `TEST_FIXTURE` records. It is not a predictive CLD model, a biological dataset, a public screening service or a validated manufacturing quality system.

## Manufacturing context

| Term | Meaning | Relevance |
| --- | --- | --- |
| CLD | Cell line development | Our initial focus is CHO clone screening decision support. |
| USP | Upstream processing | Cell culture and production processes. |
| DSP | Downstream processing | Product recovery and purification. |
| QC | Quality control | Testing and assessment of quality attributes. |
| QA | Quality assurance | Processes and evidence that support confidence in quality. |

These terms provide context. This example does not implement or establish validated capabilities across CLD, USP, DSP, QC or QA.

## What the example checks

- Required record fields, unique identifiers and a nonempty declared source.
- Timezone-aware timestamps and the ordering `observed_at <= available_at <= cutoff`.
- Explicit eligibility, an exclusion reason for excluded records, the expected test unit and finite numeric values.
- In a separate library helper, selected test-run and preservation declarations, including count reconciliation and ordered timestamps.

Excluded records stay in the registry and do not enter `eligible_ids`. Missing or invalid evidence fails a software check; it does not mean that a biological clone should be dropped. A declared source is not proof of provenance or authenticity.

`qc_example.py` checks the artificial records. `mandatory_evidence.py` is a separate callback-based library helper, exercised by the tests; the records CLI does not invoke it. The helper does not authenticate an evidence producer, verify referenced logs or files, enforce freshness, or independently prove that tests ran.

## Run locally

Python 3.9 or later; standard library only. No package installation, credentials or network service is required. From the repository root:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B qc_example.py fixtures/TEST_FIXTURE_records.json --cutoff 2026-01-03T00:00:00+00:00
```

The suite contains **24 tests**. The second command exits with status 0 and prints the following result (whitespace may differ):

```json
{
  "status": "PASS",
  "registry_records": 2,
  "eligible_ids": ["TEST_A"],
  "findings": [],
  "scientific_interpretation": "NONE_TEST_FIXTURE",
  "release_authorised": false
}
```

Invalid or nonpassing input produces exit status 2. Check the overall `status` before using a result: a failing registry can still list valid eligible records from other rows. `release_authorised` is always `false`; this software does not grant scientific, manufacturing or release approval.

## Repository contents

```text
LICENSE
README.md
docs/METHODS_AND_LIMITATIONS.md
fixtures/TEST_FIXTURE_records.json
mandatory_evidence.py
qc_example.py
tests/test_example.py
```

See [Methods, provenance and limitations](docs/METHODS_AND_LIMITATIONS.md) for the exact scope and evidence limits. Software test success establishes neither biological validity nor predictive performance, regulatory suitability or commercial benefit.

## License and contact

The files included here are licensed under the [MIT License](LICENSE). Proprietary scientific engines, models, unpublished methods and private data are not included in this repository or its license grant.

Visit [MatrixBioservices](https://matrixbioservices.com) for consultation. Do not post confidential experimental data, customer information or credentials in public issues.

## Attribution

OpenAI's ChatGPT and Codex assisted with software development and documentation. MatrixBioservices retains responsibility for the content and its review.

MatrixBioservices is not affiliated with or endorsed by OpenAI.
