#!/bin/bash
# validate_test_data.sh
# Pre-Reporting Validation Script for E2E Testing
#
# Usage: bash validate_test_data.sh <test-reports-directory>
# Example: bash validate_test_data.sh test-reports/2025-11-13_143022

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get test directory from argument or use latest
if [ -n "$1" ]; then
    TEST_DIR="$1"
else
    # Find the latest timestamped directory
    LATEST=$(ls -t test-reports/ 2>/dev/null | head -1)
    if [ -z "$LATEST" ]; then
        echo -e "${RED}❌ ERROR: No test reports directory found${NC}"
        exit 1
    fi
    TEST_DIR="test-reports/$LATEST"
fi

echo "=========================================="
echo "Test Data Validation"
echo "Directory: $TEST_DIR"
echo "=========================================="
echo ""

FAIL_COUNT=0
WARN_COUNT=0

# Check if directory exists
if [ ! -d "$TEST_DIR" ]; then
    echo -e "${RED}❌ ERROR: Directory not found: $TEST_DIR${NC}"
    exit 1
fi

# ============================================
# 1. Test Case Status Verification
# ============================================
echo -e "${BLUE}1️⃣ Checking test case statuses...${NC}"

if [ ! -d "$TEST_DIR/test-case-reports" ]; then
    echo -e "   ${RED}❌ FAIL: test-case-reports/ directory does not exist${NC}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
else
    # Count test cases
    TOTAL_TC=$(find "$TEST_DIR/test-case-reports" -name "*.md" 2>/dev/null | wc -l)
    echo "   Total test cases: $TOTAL_TC"

    if [ "$TOTAL_TC" -eq 0 ]; then
        echo -e "   ${RED}❌ FAIL: No test case reports found${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    else
        # Check for pending/incomplete statuses
        PENDING_CASES=$(grep -il "status.*pending\|status.*in progress" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)

        if [ "$PENDING_CASES" -gt 0 ]; then
            echo -e "   ${RED}❌ FAIL: $PENDING_CASES test case(s) in pending/in-progress state${NC}"
            echo -e "   ${YELLOW}Action required: Complete or re-execute these test cases${NC}"

            # List pending cases
            grep -il "status.*pending\|status.*in progress" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | while read file; do
                echo -e "   ${YELLOW}   - $(basename "$file")${NC}"
            done

            FAIL_COUNT=$((FAIL_COUNT + 1))
        else
            echo -e "   ${GREEN}✅ PASS: All test cases have final status${NC}"
        fi

        # Check for missing status fields
        NO_STATUS=$(grep -L "^\*\*Status\*\*:" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)
        if [ "$NO_STATUS" -gt 0 ]; then
            echo -e "   ${RED}❌ FAIL: $NO_STATUS test case(s) missing status field${NC}"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi

        # Count by status
        PASS_COUNT=$(grep -il "status.*pass" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)
        FAIL_TC_COUNT=$(grep -il "status.*fail" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)
        BLOCKED_COUNT=$(grep -il "status.*blocked" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)
        NOT_RUN_COUNT=$(grep -il "status.*not run" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)

        echo "   Status distribution:"
        echo "   - Pass: $PASS_COUNT"
        echo "   - Fail: $FAIL_TC_COUNT"
        echo "   - Blocked: $BLOCKED_COUNT"
        echo "   - Not Run: $NOT_RUN_COUNT"
    fi
fi
echo ""

# ============================================
# 2. Directory Structure Compliance
# ============================================
echo -e "${BLUE}2️⃣ Checking directory structure...${NC}"

# Check required subdirectories
REQUIRED_DIRS=("test-case-reports" "screenshots" "logs")
MISSING_DIRS=0

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$TEST_DIR/$dir" ]; then
        echo -e "   ${YELLOW}⚠️ WARNING: Missing directory: $dir/${NC}"
        echo -e "   ${YELLOW}Creating: $TEST_DIR/$dir${NC}"
        mkdir -p "$TEST_DIR/$dir"
        WARN_COUNT=$((WARN_COUNT + 1))
        MISSING_DIRS=$((MISSING_DIRS + 1))
    fi
done

if [ "$MISSING_DIRS" -eq 0 ]; then
    echo -e "   ${GREEN}✅ PASS: All required subdirectories exist${NC}"
fi

# Check for misplaced files
MISPLACED_TC=$(find "$TEST_DIR" -maxdepth 1 -name "TC-*.md" 2>/dev/null | wc -l)
MISPLACED_DEFECTS=$(find "$TEST_DIR" -maxdepth 1 -name "DEFECT-*.md" 2>/dev/null | wc -l)
MISPLACED_SCREENSHOTS=$(find "$TEST_DIR" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" \) 2>/dev/null | wc -l)

if [ "$MISPLACED_TC" -gt 0 ]; then
    echo -e "   ${YELLOW}⚠️ WARNING: $MISPLACED_TC test case(s) at root level${NC}"
    echo -e "   ${YELLOW}Moving to test-case-reports/${NC}"
    find "$TEST_DIR" -maxdepth 1 -name "TC-*.md" -exec mv {} "$TEST_DIR/test-case-reports/" \; 2>/dev/null
    WARN_COUNT=$((WARN_COUNT + 1))
fi

if [ "$MISPLACED_DEFECTS" -gt 0 ]; then
    echo -e "   ${YELLOW}⚠️ WARNING: $MISPLACED_DEFECTS defect report(s) at root level${NC}"
    echo -e "   ${YELLOW}Moving to defect-reports/${NC}"
    mkdir -p "$TEST_DIR/defect-reports"
    find "$TEST_DIR" -maxdepth 1 -name "DEFECT-*.md" -exec mv {} "$TEST_DIR/defect-reports/" \; 2>/dev/null
    WARN_COUNT=$((WARN_COUNT + 1))
fi

if [ "$MISPLACED_SCREENSHOTS" -gt 0 ]; then
    echo -e "   ${YELLOW}⚠️ WARNING: $MISPLACED_SCREENSHOTS screenshot(s) at root level${NC}"
    echo -e "   ${YELLOW}Moving to screenshots/${NC}"
    find "$TEST_DIR" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" \) -exec mv {} "$TEST_DIR/screenshots/" \; 2>/dev/null
    WARN_COUNT=$((WARN_COUNT + 1))
fi

if [ "$MISPLACED_TC" -eq 0 ] && [ "$MISPLACED_DEFECTS" -eq 0 ] && [ "$MISPLACED_SCREENSHOTS" -eq 0 ]; then
    echo -e "   ${GREEN}✅ PASS: All files in correct subdirectories${NC}"
fi

# Display file distribution
echo "   File distribution:"
echo "   - Test cases:     $(find "$TEST_DIR/test-case-reports" -name "*.md" 2>/dev/null | wc -l)"
echo "   - Defect reports: $(find "$TEST_DIR/defect-reports" -name "*.md" 2>/dev/null | wc -l)"
echo "   - Screenshots:    $(find "$TEST_DIR/screenshots" -type f \( -name "*.png" -o -name "*.jpg" \) 2>/dev/null | wc -l)"
echo "   - Log files:      $(find "$TEST_DIR/logs" -type f 2>/dev/null | wc -l)"
echo ""

# ============================================
# 3. Evidence Completeness
# ============================================
echo -e "${BLUE}3️⃣ Checking evidence completeness...${NC}"

SCREENSHOTS_COUNT=$(find "$TEST_DIR/screenshots" -type f \( -name "*.png" -o -name "*.jpg" \) 2>/dev/null | wc -l)
LOGS_COUNT=$(find "$TEST_DIR/logs" -type f 2>/dev/null | wc -l)

echo "   Total screenshots: $SCREENSHOTS_COUNT"
echo "   Total log files:   $LOGS_COUNT"

# Check failed/blocked test cases for evidence
if [ "$TOTAL_TC" -gt 0 ]; then
    FAILED_BLOCKED=$(grep -l "Status.*\(Fail\|Blocked\)" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null | wc -l)

    if [ "$FAILED_BLOCKED" -gt 0 ]; then
        echo "   Failed/blocked test cases: $FAILED_BLOCKED"

        # Check if failed cases have screenshots
        FAILED_WITHOUT_SCREENSHOTS=0
        for case_file in $(grep -l "Status.*\(Fail\|Blocked\)" "$TEST_DIR/test-case-reports/"*.md 2>/dev/null); do
            tc_id=$(grep "^# TC-" "$case_file" | sed 's/^# \(TC-[0-9]*\).*/\1/' | head -1)
            if [ -n "$tc_id" ]; then
                screenshot_count=$(find "$TEST_DIR/screenshots" -name "*${tc_id}*" 2>/dev/null | wc -l)
                if [ "$screenshot_count" -eq 0 ]; then
                    echo -e "   ${YELLOW}⚠️ WARNING: $tc_id (failed/blocked) has no screenshots${NC}"
                    FAILED_WITHOUT_SCREENSHOTS=$((FAILED_WITHOUT_SCREENSHOTS + 1))
                    WARN_COUNT=$((WARN_COUNT + 1))
                fi
            fi
        done

        if [ "$FAILED_WITHOUT_SCREENSHOTS" -eq 0 ]; then
            echo -e "   ${GREEN}✅ PASS: All failed/blocked cases have screenshots${NC}"
        fi
    fi
fi

# Check for screenshots without TC-ID (won't auto-link)
SCREENSHOTS_NO_TC=$(find "$TEST_DIR/screenshots" -type f \( -name "*.png" -o -name "*.jpg" \) \
    ! -iname "*tc-*" ! -iname "*tc[0-9]*" 2>/dev/null | wc -l)

if [ "$SCREENSHOTS_NO_TC" -gt 0 ]; then
    echo -e "   ${YELLOW}⚠️ WARNING: $SCREENSHOTS_NO_TC screenshot(s) don't include test case ID${NC}"
    echo -e "   ${YELLOW}These won't auto-link to test cases in HTML report${NC}"
    echo -e "   ${YELLOW}💡 TIP: Rename to include TC-ID: 05_TC-003_error.png${NC}"
    WARN_COUNT=$((WARN_COUNT + 1))
fi

# Check for API error logs
API_LOGS=$(find "$TEST_DIR/logs" -name "api_error_*" 2>/dev/null | wc -l)
if [ "$API_LOGS" -gt 0 ]; then
    echo "   API error logs found: $API_LOGS"

    # Verify naming pattern
    for log in $(find "$TEST_DIR/logs" -name "api_error_*" 2>/dev/null); do
        basename_log=$(basename "$log")
        if [[ ! "$basename_log" =~ api_error_TC-[0-9]+ ]]; then
            echo -e "   ${YELLOW}⚠️ WARNING: API log doesn't follow naming pattern: $basename_log${NC}"
            echo -e "   ${YELLOW}Expected: api_error_TC-XXX_description.json${NC}"
            WARN_COUNT=$((WARN_COUNT + 1))
        fi
    done
fi

# Check for empty files
EMPTY_SCREENSHOTS=$(find "$TEST_DIR/screenshots" -type f -size 0 2>/dev/null | wc -l)
EMPTY_LOGS=$(find "$TEST_DIR/logs" -type f -size 0 2>/dev/null | wc -l)
EMPTY_TC=$(find "$TEST_DIR/test-case-reports" -type f -size 0 2>/dev/null | wc -l)

if [ "$EMPTY_SCREENSHOTS" -gt 0 ] || [ "$EMPTY_LOGS" -gt 0 ] || [ "$EMPTY_TC" -gt 0 ]; then
    echo -e "   ${RED}❌ FAIL: Found empty files:${NC}"
    [ "$EMPTY_SCREENSHOTS" -gt 0 ] && echo -e "   ${RED}   - $EMPTY_SCREENSHOTS empty screenshot(s)${NC}"
    [ "$EMPTY_LOGS" -gt 0 ] && echo -e "   ${RED}   - $EMPTY_LOGS empty log file(s)${NC}"
    [ "$EMPTY_TC" -gt 0 ] && echo -e "   ${RED}   - $EMPTY_TC empty test case(s)${NC}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
else
    echo -e "   ${GREEN}✅ PASS: No empty files detected${NC}"
fi
echo ""

# ============================================
# Final Summary
# ============================================
echo "=========================================="
echo "Validation Summary"
echo "=========================================="

if [ "$FAIL_COUNT" -eq 0 ] && [ "$WARN_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Your test data is complete and ready for reporting."
    echo "You can now proceed to Phase 4 (Evaluation & Reporting)."
    echo ""
    echo "Next steps:"
    echo "1. Generate test summary report (references/evaluation.md)"
    echo "2. Run: python skills/end-to-end-testing/scripts/generate_html_report.py \"$TEST_DIR\""
    exit 0
elif [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️ VALIDATION PASSED WITH WARNINGS${NC}"
    echo ""
    echo "$WARN_COUNT warning(s) found (automatically fixed or non-critical)."
    echo "You can proceed to Phase 4, but review warnings above."
    echo ""
    echo "Next steps:"
    echo "1. Review warnings and fix if needed"
    echo "2. Generate test summary report (references/evaluation.md)"
    echo "3. Run: python skills/end-to-end-testing/scripts/generate_html_report.py \"$TEST_DIR\""
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo ""
    echo "$FAIL_COUNT critical issue(s) found."
    echo "$WARN_COUNT warning(s) found."
    echo ""
    echo "DO NOT proceed to Phase 4 (Evaluation & Reporting) until all critical issues are resolved."
    echo ""
    echo "Required actions:"
    echo "1. Complete all pending test cases"
    echo "2. Ensure all test cases have explicit status"
    echo "3. Capture missing screenshots/logs for failed tests"
    echo "4. Remove or regenerate empty files"
    echo "5. Re-run this validation script"
    exit 1
fi
