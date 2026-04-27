---
name: end-to-end-testing
description: Systematic E2E testing workflow with evidence capture and reporting. Use when running integration tests, validating complete user flows, capturing test evidence, or generating test reports.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# End-to-End Testing

Systematic E2E testing workflow for complete system validation with evidence capture.

## When to Apply

Reference this skill when:
- Running integration or E2E tests
- Validating complete user flows
- Capturing test evidence (screenshots, logs)
- Generating test reports
- Documenting defects systematically

## How It Works

### Phase 1: Preparation
- Gather environment information
- Verify test credentials
- Set up test data

### Phase 2: Planning & Design
- Smoke testing
- Test case design
- Priority assignment

### Phase 3: Execution
- Execute test cases
- Capture evidence (screenshots)
- Document defects

### Phase 4: Pre-Reporting Validation (CRITICAL)
- **MANDATORY** before reporting
- Verify all evidence captured
- Validate defect documentation
- Cross-check test results

### Phase 5: Reporting
- Generate comprehensive reports
- Create HTML viewer
- Archive evidence

## Output Structure

```
test-reports/
└── YYYY-MM-DD_HHMMSS/
    ├── Test_Report_Viewer.html
    ├── test-case-reports/
    ├── defect-reports/
    ├── test-summary-report.md
    ├── screenshots/
    └── logs/
```

## Usage

```bash
# Generate HTML report
python scripts/generate-html-report.py --input test-results/

# Validate test data
./scripts/validate-test-data.sh
```

## Templates

- [Defect Report Template](./assets/templates/defect-report.md)
- [Test Case Report Template](./assets/templates/test-case-report.md)
- [Test Summary Template](./assets/templates/test-summary-report.md)

## References

- [Preparation](./references/preparation.md)
- [Planning & Design](./references/planning-design.md)
- [Execution](./references/execution.md)
- [Validation](./references/validation.md)
- [Reporting](./references/reporting.md)
