---
name: Pre-Reporting Validation
description: Mandatory validation checklist before generating test summary reports
---

# Pre-Reporting Validation Phase

## Overview

This critical phase ensures data completeness and integrity before generating test summary reports. **Do NOT proceed to Phase 4 (Evaluation & Reporting) until all validation checks pass.**

Incomplete or inconsistent test data will result in inaccurate reports and invalid metrics. This phase prevents common issues such as missing test case statuses, pending cases, misplaced files, and incomplete evidence collection.

---

## Validation Workflow

Execute the following validations in order:

### 1. Test Case Status Verification

**Objective**: Confirm all test cases have explicit, final status values.

**Valid Statuses**:
- ✅ **Pass** - Test case executed successfully, all assertions passed
- ❌ **Fail** - Test case executed but failed assertions or requirements
- ⚠️ **Blocked** - Test case could not be executed due to blocker (environment issue, dependency failure)
- ⏭️ **Not Run** - Test case was not executed (out of scope, time constraints)

**Invalid/Incomplete Statuses**:
- ❌ "Pending" - Must be resolved before reporting
- ❌ "In Progress" - Must complete execution or mark as Not Run
- ❌ Empty/null status - Must assign explicit status
- ❌ "Unknown" - Must investigate and assign correct status

#### Validation Steps

1. **List all test case reports**:
   ```bash
   ls -1 test-reports/YYYY-MM-DD_HHMMSS/test-case-reports/*.md
   ```

2. **Check status in each test case report**:
   ```bash
   for file in test-reports/YYYY-MM-DD_HHMMSS/test-case-reports/*.md; do
       echo "Checking: $file"
       grep -i "^\*\*Status\*\*:" "$file" || echo "⚠️ WARNING: No status found"
   done
   ```

3. **Identify test cases with invalid statuses**:
   ```bash
   grep -l "Status.*Pending\|Status.*In Progress\|Status.*Unknown" \
       test-reports/YYYY-MM-DD_HHMMSS/test-case-reports/*.md
   ```

4. **For each test case with invalid status**:
   - **If execution was incomplete**:
     - Re-execute the test case to completion
     - Update status based on actual result
   - **If blocked by environment issue**:
     - Mark status as "Blocked"
     - Document blocker reason in test case report
   - **If not executed due to time/scope constraints**:
     - Mark status as "Not Run"
     - Document reason in test case report

#### Expected Outcome

✅ **Pass Criteria**: All test case reports contain one of the four valid statuses (Pass, Fail, Blocked, Not Run)

❌ **Fail Criteria**: Any test case has "Pending", "In Progress", empty, or invalid status

---

### 2. Pending Case Re-check

**Objective**: Resolve all test cases that are in pending or incomplete state.

**Common Reasons for Pending Status**:
- Test execution interrupted (timeout, crash)
- Waiting for data or resource
- Unclear test steps or requirements
- Environment became unavailable mid-test

#### Validation Steps

1. **Identify all pending test cases**:
   ```bash
   # Search for "pending" status (case-insensitive)
   grep -il "status.*pending" test-reports/YYYY-MM-DD_HHMMSS/test-case-reports/*.md
   ```

2. **For each pending test case**:
   - **Review the test case report**: Identify why execution is incomplete
   - **Check prerequisites**: Verify environment, data, and dependencies are available
   - **Re-execute the test case**: Complete the test execution
   - **Update status**: Change from "Pending" to final status (Pass/Fail/Blocked)
   - **Add execution notes**: Document what was completed and final result

3. **Verify no test cases remain pending**:
   ```bash
   # This should return no results
   grep -il "status.*pending" test-reports/YYYY-MM-DD_HHMMSS/test-case-reports/*.md

   # Output should be empty
   echo "Pending test cases remaining: $(grep -il 'status.*pending' test-reports/YYYY-MM-DD_HHMMSS/test-case-reports/*.md | wc -l)"
   ```

#### Expected Outcome

✅ **Pass Criteria**: Zero test cases in pending state. All test cases have final status.

❌ **Fail Criteria**: One or more test cases remain in pending state.

**Action if Failed**: Do NOT proceed to reporting. Resolve all pending cases first.

---

### 3. Directory Structure Compliance

**Objective**: Verify all test artifacts are saved in the correct directories following the Test Reports Directory Structure.

**Expected Directory Structure**:
```
test-reports/YYYY-MM-DD_HHMMSS/
├── test-case-reports/       # All *.md test case files
├── defect-reports/          # All DEFECT-*.md files
├── screenshots/             # All *.png, *.jpg screenshot files
└── logs/                    # All *.log, *.json, *.txt log files
```

#### Validation Steps

1. **Verify timestamped directory exists**:
   ```bash
   TEST_DIR="test-reports/YYYY-MM-DD_HHMMSS"

   if [ -d "$TEST_DIR" ]; then
       echo "✅ Test directory exists: $TEST_DIR"
   else
       echo "❌ ERROR: Test directory not found: $TEST_DIR"
       exit 1
   fi
   ```

2. **Verify required subdirectories exist**:
   ```bash
   for subdir in test-case-reports defect-reports screenshots logs; do
       if [ -d "$TEST_DIR/$subdir" ]; then
           echo "✅ $subdir/ exists"
       else
           echo "⚠️ WARNING: $subdir/ does not exist"
           mkdir -p "$TEST_DIR/$subdir"
           echo "   Created: $TEST_DIR/$subdir"
       fi
   done
   ```

3. **Check for misplaced test case reports**:
   ```bash
   # Test case reports should be in test-case-reports/ only
   find "$TEST_DIR" -name "TC-*.md" -not -path "*/test-case-reports/*" 2>/dev/null

   # If any found, move them:
   find "$TEST_DIR" -name "TC-*.md" -not -path "*/test-case-reports/*" \
       -exec mv {} "$TEST_DIR/test-case-reports/" \; 2>/dev/null
   ```

4. **Check for misplaced defect reports**:
   ```bash
   # Defect reports should be in defect-reports/ only
   find "$TEST_DIR" -name "DEFECT-*.md" -not -path "*/defect-reports/*" 2>/dev/null

   # If any found, move them:
   find "$TEST_DIR" -name "DEFECT-*.md" -not -path "*/defect-reports/*" \
       -exec mv {} "$TEST_DIR/defect-reports/" \; 2>/dev/null
   ```

5. **Check for misplaced screenshots**:
   ```bash
   # Screenshots should be in screenshots/ only
   find "$TEST_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) \
       -not -path "*/screenshots/*" 2>/dev/null

   # If any found, move them:
   find "$TEST_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) \
       -not -path "*/screenshots/*" \
       -exec mv {} "$TEST_DIR/screenshots/" \; 2>/dev/null
   ```

6. **Check for misplaced log files**:
   ```bash
   # Log files should be in logs/ only
   find "$TEST_DIR" -type f \( -name "*.log" -o -name "*.json" -o -name "*.txt" \) \
       -not -path "*/logs/*" \
       -not -name "test-summary-report.md" \
       -not -name "TC-*.md" \
       -not -name "DEFECT-*.md" 2>/dev/null

   # If any found, move them:
   find "$TEST_DIR" -type f \( -name "*.log" -o -name "*.json" -o -name "*.txt" \) \
       -not -path "*/logs/*" \
       -not -name "test-summary-report.md" \
       -exec mv {} "$TEST_DIR/logs/" \; 2>/dev/null
   ```

7. **Verify file counts**:
   ```bash
   echo "📊 File Distribution:"
   echo "   Test cases:    $(find "$TEST_DIR/test-case-reports" -name "*.md" | wc -l)"
   echo "   Defect reports: $(find "$TEST_DIR/defect-reports" -name "*.md" 2>/dev/null | wc -l)"
   echo "   Screenshots:   $(find "$TEST_DIR/screenshots" -type f \( -name "*.png" -o -name "*.jpg" \) | wc -l)"
   echo "   Log files:     $(find "$TEST_DIR/logs" -type f | wc -l)"
   ```

#### Expected Outcome

✅ **Pass Criteria**:
- All test case reports are in `test-case-reports/`
- All defect reports are in `defect-reports/` (if any defects exist)
- All screenshots are in `screenshots/`
- All log files are in `logs/`

❌ **Fail Criteria**: Files are scattered in wrong directories or at root level

---

### 4. Evidence Completeness

**Objective**: Ensure all test cases have required evidence (screenshots, logs) properly saved and named.

**Evidence Requirements**:
- **All test cases** should have at least one screenshot showing execution
- **Failed/Blocked test cases** must have screenshots showing error state
- **API-related failures** must have API error logs saved
- **Screenshot filenames** should include test case ID for automatic linking
- **API log filenames** must follow pattern `api_error_TC-XXX_description.json`

#### Validation Steps

1. **Check for test cases without screenshots**:
   ```bash
   # Get list of all test case IDs
   TEST_CASES=$(grep -h "^# TC-" "$TEST_DIR/test-case-reports/"*.md | \
                sed 's/^# \(TC-[0-9]*\).*/\1/' | sort -u)

   # Check if each test case has at least one screenshot
   echo "Checking screenshot coverage..."
   for tc in $TEST_CASES; do
       screenshot_count=$(find "$TEST_DIR/screenshots" -name "*${tc}*" | wc -l)
       if [ "$screenshot_count" -eq 0 ]; then
           echo "⚠️ WARNING: $tc has no screenshots"
       else
           echo "✅ $tc has $screenshot_count screenshot(s)"
       fi
   done
   ```

2. **Check failed/blocked test cases for evidence**:
   ```bash
   # Identify failed/blocked test cases
   FAILED_CASES=$(grep -l "Status.*\(Fail\|Blocked\)" "$TEST_DIR/test-case-reports/"*.md)

   for case_file in $FAILED_CASES; do
       tc_id=$(grep "^# TC-" "$case_file" | sed 's/^# \(TC-[0-9]*\).*/\1/')

       # Check for screenshots
       screenshot_count=$(find "$TEST_DIR/screenshots" -name "*${tc_id}*" | wc -l)
       if [ "$screenshot_count" -eq 0 ]; then
           echo "❌ CRITICAL: Failed/blocked case $tc_id has NO screenshots"
       fi

       # Check for API logs if it's an API-related failure
       if grep -q "API" "$case_file"; then
           api_log_count=$(find "$TEST_DIR/logs" -name "api_error_${tc_id}_*" | wc -l)
           if [ "$api_log_count" -eq 0 ]; then
               echo "⚠️ WARNING: API failure in $tc_id but no API error log found"
           fi
       fi
   done
   ```

3. **Validate screenshot naming conventions**:
   ```bash
   # Check if screenshots follow naming patterns
   echo "Checking screenshot naming patterns..."

   # Good patterns: 05_TC-003_error.png, 07_tc11_list.png
   # Bad patterns: screenshot1.png, error.png (no TC-ID)

   screenshots_without_tc=$(find "$TEST_DIR/screenshots" -type f \
       \( -name "*.png" -o -name "*.jpg" \) \
       ! -name "*TC-*" ! -name "*tc*" 2>/dev/null)

   if [ -n "$screenshots_without_tc" ]; then
       echo "⚠️ WARNING: Some screenshots don't include test case ID:"
       echo "$screenshots_without_tc"
       echo ""
       echo "💡 TIP: Rename screenshots to include TC-ID for automatic linking:"
       echo "   Example: mv screenshot.png 05_TC-003_error.png"
   fi
   ```

4. **Validate API log naming conventions**:
   ```bash
   # Check API error logs follow required pattern
   echo "Checking API error log naming patterns..."

   # Required pattern: api_error_TC-XXX_description.json
   api_logs=$(find "$TEST_DIR/logs" -name "api_error_*" 2>/dev/null)

   if [ -n "$api_logs" ]; then
       for log in $api_logs; do
           basename_log=$(basename "$log")
           if [[ ! "$basename_log" =~ api_error_TC-[0-9]+ ]]; then
               echo "⚠️ WARNING: API log doesn't follow naming pattern: $basename_log"
               echo "   Expected: api_error_TC-XXX_description.json"
           fi
       done
   fi
   ```

5. **Check for empty or corrupted files**:
   ```bash
   # Check for empty screenshot files
   find "$TEST_DIR/screenshots" -type f -size 0 -exec echo "❌ ERROR: Empty file: {}" \;

   # Check for empty log files
   find "$TEST_DIR/logs" -type f -size 0 -exec echo "⚠️ WARNING: Empty log: {}" \;

   # Check for empty test case reports
   find "$TEST_DIR/test-case-reports" -type f -size 0 -exec echo "❌ CRITICAL: Empty test case: {}" \;
   ```

#### Expected Outcome

✅ **Pass Criteria**:
- All test cases have at least one screenshot
- Failed/blocked test cases have error screenshots and API logs (if applicable)
- Screenshot filenames include test case IDs for automatic linking
- API error logs follow naming pattern `api_error_TC-XXX_description.json`
- No empty or corrupted files

❌ **Fail Criteria**:
- Missing screenshots for test cases (especially failed/blocked ones)
- Missing API logs for API-related failures
- Poor screenshot naming (no TC-ID) preventing automatic linking
- Empty or corrupted files

**Action if Failed**: Capture missing evidence before proceeding to reporting.

---

## Validation Summary Checklist

Before proceeding to Phase 4 (Evaluation & Reporting), confirm:

- [ ] ✅ All test cases have explicit final status (Pass/Fail/Blocked/Not Run)
- [ ] ✅ Zero test cases remain in pending or in-progress state
- [ ] ✅ All files are organized in correct subdirectories
- [ ] ✅ Test case reports are in `test-case-reports/`
- [ ] ✅ Defect reports are in `defect-reports/`
- [ ] ✅ Screenshots are in `screenshots/`
- [ ] ✅ Log files are in `logs/`
- [ ] ✅ All test cases have at least one screenshot
- [ ] ✅ Failed/blocked test cases have error evidence (screenshots + API logs)
- [ ] ✅ Screenshot filenames include test case IDs (e.g., `05_TC-003_error.png`)
- [ ] ✅ API error logs follow naming pattern (`api_error_TC-XXX_description.json`)
- [ ] ✅ No empty or corrupted files exist

**If ALL checkboxes are checked**: ✅ **PROCEED to Phase 4 (Evaluation & Reporting)**

**If ANY checkbox is unchecked**: ❌ **DO NOT PROCEED. Resolve issues first.**

---

## Automated Validation Script (Optional)

For convenience, you can create a validation script:

```bash
#!/bin/bash
# validate_test_data.sh

TEST_DIR="${1:-test-reports/$(ls -t test-reports/ | head -1)}"

echo "=========================================="
echo "Test Data Validation"
echo "Directory: $TEST_DIR"
echo "=========================================="
echo ""

FAIL_COUNT=0

# 1. Test Case Status Check
echo "1️⃣ Checking test case statuses..."
PENDING_CASES=$(grep -il "status.*pending\|status.*in progress" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)
if [ "$PENDING_CASES" -gt 0 ]; then
    echo "   ❌ FAIL: $PENDING_CASES test case(s) in pending state"
    FAIL_COUNT=$((FAIL_COUNT + 1))
else
    echo "   ✅ PASS: All test cases have final status"
fi
echo ""

# 2. Directory Structure Check
echo "2️⃣ Checking directory structure..."
REQUIRED_DIRS=("test-case-reports" "screenshots" "logs")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$TEST_DIR/$dir" ]; then
        echo "   ❌ FAIL: Missing directory: $dir/"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

MISPLACED_TC=$(find "$TEST_DIR" -maxdepth 1 -name "TC-*.md" 2>/dev/null | wc -l)
MISPLACED_SCREENSHOTS=$(find "$TEST_DIR" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" \) 2>/dev/null | wc -l)

if [ "$MISPLACED_TC" -gt 0 ] || [ "$MISPLACED_SCREENSHOTS" -gt 0 ]; then
    echo "   ⚠️ WARNING: $MISPLACED_TC test case(s) and $MISPLACED_SCREENSHOTS screenshot(s) in wrong location"
    echo "   (Can be auto-fixed by moving to correct directories)"
fi

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "   ✅ PASS: Directory structure is correct"
fi
echo ""

# 3. Evidence Completeness Check
echo "3️⃣ Checking evidence completeness..."
TOTAL_TEST_CASES=$(find "$TEST_DIR/test-case-reports" -name "*.md" | wc -l)
FAILED_CASES=$(grep -l "Status.*\(Fail\|Blocked\)" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)
SCREENSHOTS_COUNT=$(find "$TEST_DIR/screenshots" -type f \( -name "*.png" -o -name "*.jpg" \) 2>/dev/null | wc -l)

echo "   Total test cases: $TOTAL_TEST_CASES"
echo "   Failed/blocked cases: $FAILED_CASES"
echo "   Total screenshots: $SCREENSHOTS_COUNT"

if [ "$SCREENSHOTS_COUNT" -lt "$TOTAL_TEST_CASES" ]; then
    echo "   ⚠️ WARNING: Not all test cases have screenshots (recommend at least one per test)"
fi

if [ "$FAILED_CASES" -gt 0 ]; then
    # Check if failed cases have evidence
    FAILED_WITHOUT_EVIDENCE=0
    for case_file in $(grep -l "Status.*\(Fail\|Blocked\)" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null); do
        tc_id=$(grep "^# TC-" "$case_file" | sed 's/^# \(TC-[0-9]*\).*/\1/')
        screenshot_count=$(find "$TEST_DIR/screenshots" -name "*${tc_id}*" 2>/dev/null | wc -l)
        if [ "$screenshot_count" -eq 0 ]; then
            FAILED_WITHOUT_EVIDENCE=$((FAILED_WITHOUT_EVIDENCE + 1))
        fi
    done

    if [ "$FAILED_WITHOUT_EVIDENCE" -gt 0 ]; then
        echo "   ❌ FAIL: $FAILED_WITHOUT_EVIDENCE failed/blocked case(s) have NO screenshots"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    else
        echo "   ✅ PASS: All failed/blocked cases have screenshots"
    fi
fi
echo ""

# Final Result
echo "=========================================="
if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "✅ VALIDATION PASSED"
    echo "All checks passed. Ready to proceed to Phase 4 (Evaluation & Reporting)."
    exit 0
else
    echo "❌ VALIDATION FAILED"
    echo "$FAIL_COUNT critical issue(s) found. Resolve them before proceeding to reporting."
    exit 1
fi
```

**Usage**:
```bash
bash validate_test_data.sh test-reports/2025-11-13_143022
```

---

## Common Issues and Resolutions

### Issue 1: Test cases still in "Pending" status
**Cause**: Test execution was interrupted or not completed
**Resolution**:
1. Identify which test cases are pending
2. Re-execute those specific test cases
3. Update status based on execution result
4. Document reason if test cannot be completed (mark as "Blocked" or "Not Run")

### Issue 2: Screenshots in wrong directory
**Cause**: Screenshots saved to project root or wrong subdirectory during execution
**Resolution**:
```bash
# Move all screenshots to correct directory
find test-reports/YYYY-MM-DD_HHMMSS -name "*.png" -not -path "*/screenshots/*" \
    -exec mv {} test-reports/YYYY-MM-DD_HHMMSS/screenshots/ \;
```

### Issue 3: Missing API error logs for failed tests
**Cause**: Forgot to capture API logs during test execution
**Resolution**:
1. Re-execute the failed test case
2. Capture API request/response using browser DevTools or curl
3. Save to `logs/api_error_TC-XXX_description.json`

### Issue 4: Screenshots not linking to test cases in HTML report
**Cause**: Screenshot filename doesn't include test case ID
**Resolution**:
```bash
# Rename screenshots to include TC-ID
# Example: screenshot1.png → 05_TC-003_payment_error.png
mv screenshots/screenshot1.png screenshots/05_TC-003_payment_error.png
```

---

## Next Steps

Once all validation checks pass:

1. ✅ Mark validation phase as complete
2. ✅ Proceed to Phase 4 (Evaluation & Reporting)
3. ✅ Generate test summary report using `references/evaluation.md`
4. ✅ Generate interactive HTML report using `scripts/generate_html_report.py`

**Remember**: The quality of your reports depends on the completeness and accuracy of your test data. Taking time to validate now saves debugging time later.
