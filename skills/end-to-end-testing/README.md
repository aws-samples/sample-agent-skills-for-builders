# End-to-End Testing Skill

## Overview

The End-to-End Testing skill provides a systematic workflow for running comprehensive integration and E2E tests with built-in evidence capture and professional reporting. It guides you through test preparation, planning, execution, validation, and report generation with an organized output structure.

## Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill end-to-end-testing
```

## When to Use

Reference this skill when:
- Running integration or E2E tests
- Validating complete user flows
- Capturing test evidence (screenshots, logs)
- Generating test reports
- Documenting defects systematically

## Quick Start

```bash
# Validate your test environment setup
./scripts/validate-test-data.sh

# Generate an HTML report from test results
python scripts/generate-html-report.py --input test-results/

# View the generated report in your browser
open test-reports/YYYY-MM-DD_HHMMSS/Test_Report_Viewer.html
```

## File Structure

```
end-to-end-testing/
├── SKILL.md                          # Skill definition and workflow
├── README.md                         # This file
├── scripts/
│   ├── generate-html-report.py      # Convert test results to HTML
│   └── validate-test-data.sh        # Verify test environment
├── assets/
│   └── templates/
│       ├── defect-report.md         # Template for bug documentation
│       ├── test-case-report.md      # Template for test results
│       └── test-summary-report.md   # Template for test summaries
└── references/
    ├── preparation.md               # Environment setup guide
    ├── planning-design.md           # Test planning strategies
    ├── execution.md                 # Test execution best practices
    ├── validation.md                # Pre-reporting validation checklist
    └── reporting.md                 # Report generation guide
```

## Prerequisites

Before using this skill, ensure you have:

- A test environment that can be accessed and configured
- Test data and credentials available (keep these secure)
- Python 3.7+ (for HTML report generation)
- Bash shell access (for validation scripts)
- Screenshot/evidence capture tools for your target platform
- At least one test framework set up (Selenium, Playwright, Cypress, etc.)

## Workflow Overview

### Phase 1: Preparation
Gather environment information, verify test credentials, and set up test data.

**Reference:** See [preparation.md](./references/preparation.md) for detailed steps.

### Phase 2: Planning & Design
Conduct smoke testing, design test cases, and assign priorities.

**Reference:** See [planning-design.md](./references/planning-design.md) for strategies.

### Phase 3: Execution
Execute test cases, capture evidence, and document any defects found.

**Reference:** See [execution.md](./references/execution.md) for best practices.

### Phase 4: Pre-Reporting Validation (CRITICAL)
Before generating reports, verify all evidence is captured and defects are properly documented.

**Reference:** See [validation.md](./references/validation.md) for the validation checklist.

### Phase 5: Reporting
Generate comprehensive reports with HTML viewer and archive all evidence.

**Reference:** See [reporting.md](./references/reporting.md) for detailed instructions.

## Output Structure

Test reports are automatically organized with timestamps:

```
test-reports/
└── 2024-04-24_143022/
    ├── Test_Report_Viewer.html       # Interactive HTML report
    ├── test-case-reports/            # Individual test case results
    ├── defect-reports/               # Bug documentation
    ├── test-summary-report.md        # Markdown summary
    ├── screenshots/                  # Evidence capture
    └── logs/                         # Test execution logs
```

## Templates

Use these templates when documenting test results:

- **[Defect Report](./assets/templates/defect-report.md)** - Standard format for bug documentation
- **[Test Case Report](./assets/templates/test-case-report.md)** - Format for individual test results
- **[Test Summary](./assets/templates/test-summary-report.md)** - Overall testing summary

## Usage Examples

### Generate a Test Report

```bash
python scripts/generate-html-report.py --input test-results/
```

### Validate Test Environment

```bash
./scripts/validate-test-data.sh
```

### Document a Defect

1. Copy the defect report template
2. Fill in defect details, severity, steps to reproduce
3. Attach screenshots and logs
4. Place in `test-reports/[TIMESTAMP]/defect-reports/`

## Additional Resources

For detailed guidance on each workflow phase, see:

- [Preparation Guide](./references/preparation.md)
- [Planning & Design Guide](./references/planning-design.md)
- [Execution Guide](./references/execution.md)
- [Validation Guide](./references/validation.md)
- [Reporting Guide](./references/reporting.md)

## License

MIT - See LICENSE file for details.
