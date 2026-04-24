---
name: Evaluation & Reporting
description: Guidelines for generating comprehensive test summary reports, calculating metrics, and providing recommendations
---

# Evaluation & Reporting Phase

## Overview

Generate comprehensive test summary reports that provide stakeholders with clear insights into test execution results, system quality assessment, and actionable recommendations. This phase synthesizes all testing activities into executive-level documentation.

## Phase Activities

### 1. Data Collection & Analysis

Gather all test execution data before report generation:

**Required Data Sources**:
- Detailed test case reports with execution status
- All defect reports with current status
- Test environment configuration logs
- Test execution timeline and effort tracking
- Coverage analysis against requirements

**Analysis Tasks**:
- Calculate test execution statistics
- Analyze defect distribution by severity and module
- Assess test coverage completeness
- Identify high-risk areas based on failure patterns
- Evaluate environment stability issues

---

### 2. Test Summary Report Structure

The **System Test Summary Report** is the primary deliverable of this phase. Use the template at `assets/templates/test-summary-report.md` as the foundation.

#### Required Sections

##### Section 1: Executive Summary
**Purpose**: Provide non-technical stakeholders with quick assessment
**Content**:
- Testing scope and objectives (2-3 sentences)
- Key findings and overall quality assessment
- Go/no-go recommendation with justification

**Guidelines**:
- Keep it concise (200-300 words maximum)
- Avoid technical jargon
- Lead with the conclusion, then support with evidence

##### Section 2: Test Execution Statistics
**Purpose**: Quantify testing effort and results
**Content**:
- Total test cases vs. executed test cases
- Pass/fail/blocked/not run counts and percentages
- Timeline showing start/end dates for each phase

**Metrics to Calculate**:
```
Pass Rate = (Passed Test Cases / Total Executed) × 100%
Execution Rate = (Executed Test Cases / Total Test Cases) × 100%
Defect Density = Total Defects Found / Total Test Cases Executed
```

##### Section 3: Test Results by Module
**Purpose**: Identify which functional areas are stable vs. problematic
**Content**: Breakdown of test results per module with pass rates

**Analysis Guidelines**:
- Modules with <80% pass rate require attention
- Modules with 100% blocked tests indicate environmental issues
- Compare pass rates across modules to identify patterns

##### Section 4: Defect Summary
**Purpose**: Communicate quality issues to development and management
**Content**:
- Total defects by severity (S1/S2/S3/S4)
- Defect status distribution (New/Assigned/In Progress/Resolved/Closed)
- Detailed table of Critical (S1) and Major (S2) defects

**Criticality Assessment**:
- **Release Blockers**: Any unresolved S1 defects
- **High Risk**: Multiple unresolved S2 defects in core functionality
- **Acceptable**: Only S3/S4 defects remaining with workarounds

##### Section 5: Test Coverage Analysis
**Purpose**: Identify gaps in testing scope
**Content**:
- Functional coverage by requirement area
- Coverage gaps with explanations
- Untested scenarios due to blockers or time constraints

**Coverage Assessment Criteria**:
- **Fully Covered**: All requirements have corresponding test cases, all executed
- **Partially Covered**: Some requirements tested, others not executed or missing tests
- **Not Covered**: Requirements without test cases or completely untested

##### Section 6: Environment & Infrastructure
**Purpose**: Document test environment configuration for reproducibility
**Content**:
- AWS configuration (profile, region, stack details)
- Portal and database versions
- Environment issues encountered during testing

**Include**:
- Any infrastructure instability
- Configuration changes during testing
- Access or permission issues

##### Section 7: Risk Assessment
**Purpose**: Highlight areas requiring attention before release
**Content**:
- High-risk areas with unresolved defects
- Business/technical impact of each risk
- Recommended mitigation strategies

**Risk Prioritization**:
1. Critical functionality with S1/S2 defects
2. Modules with <70% pass rate
3. Untested or blocked core workflows
4. Environment instability issues

##### Section 8: Recommendations
**Purpose**: Provide actionable next steps
**Content**:
- Immediate actions required (defect fixes, retesting)
- Future improvements (automation, coverage expansion)
- Test process enhancements

**Structure Recommendations As**:
- **Short-term** (before release): Critical defect fixes, blocked test resolution
- **Medium-term** (next iteration): Minor defect fixes, coverage improvements
- **Long-term** (future sprints): Automation opportunities, process improvements

##### Section 9: Conclusion
**Purpose**: Final go/no-go decision with sign-off
**Content**:
- Overall system quality assessment
- Release readiness recommendation
- Prerequisites for production deployment
- Sign-off table for stakeholders

**Decision Criteria**:
- **Go**: No S1 defects, <3 S2 defects with workarounds, >85% pass rate
- **Conditional Go**: Few S2 defects, >80% pass rate, acceptable coverage
- **No-Go**: Any S1 defects unresolved, <75% pass rate, or major coverage gaps

##### Section 10: Appendices
**Purpose**: Link to supporting documentation
**Content**:
- Links to detailed test case reports
- Links to individual defect reports
- Links to test evidence (screenshots, logs, recordings)

---

### 3. Metrics Calculation Guide

#### Basic Metrics

**Pass Rate**:
```
Pass Rate = (Number of Passed Test Cases / Number of Executed Test Cases) × 100%
```
- Minimum acceptable: 80%
- Target: 95%+

**Execution Coverage**:
```
Execution Coverage = (Executed Test Cases / Total Planned Test Cases) × 100%
```
- Minimum acceptable: 90%
- Target: 100%

**Defect Density**:
```
Defect Density = Total Defects Found / Total Test Cases Executed
```
- Lower is better
- Industry average: 0.1 - 0.5 defects per test case

#### Advanced Metrics

**Defect Removal Efficiency (DRE)**:
```
DRE = (Defects Found in Testing / (Defects Found in Testing + Defects Found in Production)) × 100%
```
- Target: >95% (catch most defects before production)

**Test Effectiveness**:
```
Test Effectiveness = Number of Defects Found / Number of Test Cases Executed
```
- Indicates how well test cases uncover defects
- Higher values suggest better test case design

---

### 4. Report Quality Checklist

Before finalizing the test summary report, verify:

- [ ] All sections are complete with accurate data
- [ ] Metrics are calculated correctly
- [ ] Critical and major defects are highlighted
- [ ] Recommendations are specific and actionable
- [ ] Executive summary provides clear conclusion
- [ ] All links to supporting documentation work
- [ ] Sign-off section includes stakeholder names
- [ ] Report is formatted consistently and professionally
- [ ] Technical terms are explained for non-technical readers
- [ ] Charts or graphs are included if beneficial (optional)

---

### 5. HTML Report Generation

After completing the test summary report, generate an interactive HTML report viewer that consolidates all test artifacts into a single, user-friendly interface.

#### Purpose

Provide stakeholders with an interactive, visual dashboard that:
- Displays all test results in an organized, tabbed interface
- Allows easy navigation between test cases, defects, screenshots, and logs
- Eliminates the need to open multiple files to understand test results
- Provides a professional, shareable format for test documentation

#### Directory Organization

Before generating the HTML report, ensure all test artifacts are properly organized in the timestamped directory:

```
test-reports/YYYY-MM-DD_HHMMSS/
├── test-case-reports/       # All test case markdown files
├── defect-reports/          # All defect markdown files
├── test-summary-report.md   # Overall summary (already created)
├── screenshots/             # All captured screenshots
│   ├── 01_portal_home.png
│   ├── 05_TC-003_payment_error.png  # Links to TC-003
│   └── 07_tc11_package_list.png     # Links to TC-011 or TC-11
└── logs/                    # All log files
    ├── api_error_TC-021_create_environment.json  # Links to TC-021
    ├── kubernetes_logs.txt
    └── execution_timeline.log
```

**Important Naming Conventions for Automatic Linking**:

To enable automatic linking of screenshots and API logs to test cases:

1. **Screenshots** - Use one of these patterns in filenames:
   - `[number]_TC-XXX_[description].png` → Links to TC-XXX
   - `[number]_tcXX_[description].png` → Links to TC-0XX (padded)
   - Example: `05_TC-003_payment_error.png` → Displays in TC-003 test case
   - Example: `07_tc11_package_list.png` → Displays in TC-011 test case

2. **API Error Logs** - Required pattern:
   - `api_error_TC-XXX_[description].json` → Links to TC-XXX
   - Example: `api_error_TC-021_create_environment.json` → Displays in TC-021 test case
   - **Must start with `api_error_`** to be recognized as API error log
   - **Must include TC-XXX pattern** to link to correct test case

#### HTML Report Generation Methods

**Method 1: Automated Script (Recommended)**

Use the provided Python script to automatically generate the HTML report:

```bash
python skills/end-to-end-testing/scripts/generate_html_report.py test-reports/YYYY-MM-DD_HHMMSS
```

The script will:
1. Parse `test-summary-report.md` for executive summary and statistics
2. Parse all files in `test-case-reports/` for test case details
3. Parse all files in `defect-reports/` for defect information
4. Scan `screenshots/` directory for all images
5. Scan `logs/` directory for all log files
6. **Automatically link screenshots to test cases** based on filename patterns
7. **Automatically link API error logs to test cases** based on filename patterns
8. Generate `Test_Report_Viewer.html` with all data populated

**New Features**:
- **Inline Screenshots**: Screenshots are displayed directly within each test case's expanded view
- **API Error Logs**: Failed test cases automatically display their API error logs inline
- **Intelligent Linking**: Screenshots and logs are automatically associated with test cases by matching filename patterns (e.g., `05_TC-003_error.png` links to TC-003)

**Method 2: Manual Population**

If the script encounters issues or customization is needed:

1. **Copy the template**:
   ```bash
   cp skills/end-to-end-testing/assets/templates/Test_Report_Viewer.html test-reports/YYYY-MM-DD_HHMMSS/
   ```

2. **Extract data from markdown files**:
   - Read `test-summary-report.md` sections 1-2 for executive summary and statistics
   - Read each `test-case-reports/*.md` file for test case details
   - Read each `defect-reports/*.md` file for defect information

3. **Populate HTML sections**:
   - **Executive Summary**: Extract from test-summary-report.md Section 1
   - **Test Statistics**: Calculate from test case status counts
   - **Test Cases by Status**: Group test cases by Pass/Fail/Blocked/Not Run
   - **Defects**: List all defects with severity, priority, and status
   - **Screenshots**: Generate thumbnail grid from `screenshots/` directory
   - **Logs**: List all log files with download links

4. **Update relative paths**:
   - Screenshot paths: `screenshots/filename.png`
   - Defect report paths: `defect-reports/DEFECT-XXX.md`
   - Log file paths: `logs/filename.log`

#### HTML Report Structure

The generated HTML report should contain these interactive sections:

**Tab 1: Summary**
- Executive summary with key findings
- Test execution statistics (total, passed, failed, blocked)
- Test environment details
- Module-level test coverage table
- Overall pass rate visualization

**Tab 2: Passed Tests**
- List of all test cases with status "Pass"
- Expandable details for each test case
- Test case metadata (module, priority, execution time)

**Tab 3: Blocked Tests**
- List of all test cases with status "Blocked"
- Blocking reasons and dependencies
- Required actions to unblock

**Tab 4: Defects**
- All defects organized by severity (S1, S2, S3, S4)
- Defect details with links to full defect reports
- Status indicators (New, In Progress, Resolved, Closed)
- Impact assessment and priority

**Tab 5: Screenshots**
- Thumbnail grid of all captured screenshots
- Click-to-expand modal for full-size viewing
- Screenshots numbered sequentially (01_, 02_, 03_, etc.)
- Organized by test case if naming convention includes TC-ID

**Tab 6: Logs**
- List of all log files with descriptions
- Direct links to view/download logs
- Log file types: API responses, Kubernetes logs, execution timelines
- Timestamps and file sizes

#### Data Extraction Patterns

When parsing markdown files, use these patterns:

**From test-summary-report.md**:
```
Executive Summary section → Tab 1 summary text
Test Execution Statistics table → Tab 1 statistics
Module results table → Tab 1 module coverage
Defect summary → Tab 4 defect statistics
```

**From test-case-reports/*.md**:
```
File name → Test Case ID
Status field → Group into Passed/Failed/Blocked tabs
Module, Priority, Steps → Test case details
```

**From defect-reports/*.md**:
```
Defect ID, Severity, Priority → Defect listing
Description → Defect details
Status → Defect status indicator
```

**From screenshots/ directory**:
```
List all .png, .jpg, .jpeg files
Sort by filename (numerically if numbered)
Generate thumbnail links with modal view
```

**From logs/ directory**:
```
List all .log, .json, .txt files
Extract filename and size
Generate download links
```

#### HTML Generation Validation

After generating the HTML report, verify:

- [ ] All sections load without errors
- [ ] All tabs are clickable and display correct content
- [ ] Screenshot thumbnails display correctly
- [ ] Screenshot modal opens and shows full-size images
- [ ] All relative paths resolve correctly (no broken links)
- [ ] Defect report links work (if applicable)
- [ ] Statistics match the test summary report
- [ ] Test case counts are accurate
- [ ] HTML renders properly in multiple browsers (Chrome, Firefox, Safari)

#### Troubleshooting

**Issue**: Screenshots don't display
- **Solution**: Verify screenshot paths use relative paths: `screenshots/filename.png`
- **Solution**: Ensure screenshot files exist in the `screenshots/` directory

**Issue**: Statistics don't match markdown reports
- **Solution**: Recount test cases from `test-case-reports/` directory
- **Solution**: Verify all test case files have valid status fields

**Issue**: HTML layout is broken
- **Solution**: Check for JavaScript errors in browser console
- **Solution**: Verify HTML syntax is valid (no unclosed tags)

**Issue**: Log files not listed
- **Solution**: Ensure log files are in the `logs/` directory
- **Solution**: Verify file permissions allow reading

---

## Deliverables

### 1. System Test Summary Report

**Format**: Markdown document using `assets/templates/test-summary-report.md`

**Location**: `test-reports/YYYY-MM-DD_HHMMSS/test-summary-report.md`

**Distribution**:
- Project Manager (for planning and decision-making)
- Development Team Lead (for defect prioritization)
- QA Manager (for process improvement)
- Product Owner (for release decisions)
- Stakeholders (for visibility into quality)

**Timeline**: Complete within 1-2 business days after test execution concludes

### 2. Interactive HTML Report Viewer

**Format**: HTML document with embedded CSS/JavaScript

**Location**: `test-reports/YYYY-MM-DD_HHMMSS/Test_Report_Viewer.html`

**Purpose**: Provides stakeholders with a single, interactive interface to view all test results, defects, screenshots, and logs without navigating multiple files

**Distribution**:
- Share the timestamped directory via email, file share, or version control
- Recipients can open `Test_Report_Viewer.html` in any modern web browser
- All assets (screenshots, logs) are accessible via relative paths

**Timeline**: Generate immediately after completing the test summary report

---

## Best Practices

1. **Be Objective**: Present data without bias; let metrics speak
2. **Be Clear**: Use simple language and visual aids when possible
3. **Be Actionable**: Every recommendation should have a clear owner and timeline
4. **Be Complete**: Include all required sections; incomplete reports delay decisions
5. **Be Honest**: Report quality issues transparently; hiding problems creates bigger issues later

---

## Common Pitfalls to Avoid

❌ **Don't**: Sugarcoat quality issues to make results look better
✅ **Do**: Report problems honestly with mitigation plans

❌ **Don't**: Use vague statements like "most tests passed"
✅ **Do**: Provide exact numbers and percentages

❌ **Don't**: Skip the conclusion or recommendation section
✅ **Do**: Provide clear go/no-go decision with justification

❌ **Don't**: Submit report without stakeholder review
✅ **Do**: Get sign-off from key stakeholders

❌ **Don't**: Leave defects untracked or unresolved
✅ **Do**: Ensure all defects have status and assigned owners
