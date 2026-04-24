---
name: Planning & Design
description: Standards for smoke testing, detailed test case design, and test case report format
---

# Planning & Design Phase

## Overview

Validate test environment readiness through smoke testing and transform user-provided test cases into detailed, executable test case reports. This phase ensures environment stability and test case completeness before execution.

## Phase Activities

### 1. Smoke Testing

Perform quick validation checks to confirm basic system functionality.

#### Required Smoke Tests

| Test | Command/Action | Success Criteria |
|:-----|:--------------|:-----------------|
| AWS CLI Access | `aws sts get-caller-identity --profile <profile>` | Returns account ID and user ARN |
| CloudFormation Stack | `aws cloudformation describe-stacks --stack-name <name>` | Stack status is `CREATE_COMPLETE` or `UPDATE_COMPLETE` |
| Portal Accessibility | Navigate to portal URL in browser | Page loads with HTTP 200, login page visible |
| Basic Authentication | Login with test credentials | Successful authentication and redirect |

**Smoke Test Checklist**:
- [ ] AWS CLI commands execute without errors
- [ ] Stack resources are accessible
- [ ] Portal responds within acceptable time
- [ ] Test user can authenticate
- [ ] No critical infrastructure issues detected

---

### 2. Detailed Test Case Design

Transform high-level test cases into comprehensive, executable test case reports following standardized format.

## Detailed Test Case Report Format

The **Detailed Test Case Report** guides test execution with clear, traceable, and atomic test cases. Each test case must be:
- **Atomic**: Tests single functional point or scenario
- **Traceable**: Links to specific requirements
- **Reproducible**: Anyone can execute following the steps
- **Complete**: Includes all required fields

### Required Fields

| Field | Description | Criticality | Notes |
|:------|:------------|:------------|:------|
| **Case ID** | Unique identifier with project/module prefix | Required | Format: `SYS-[MODULE]-TC-[NNN]` |
| **Test Module** | Functional module being tested | Required | Examples: User Registration, Order Management |
| **Requirement ID** | Link to SRS requirement number | Required | Enables traceability |
| **Case Type** | Testing category | Required | Functional, Performance, Security, etc. |
| **Title/Objective** | Clear statement of what is being tested | Required | Brief and specific |
| **Priority** | Test importance level | Required | P1 (High), P2 (Medium), P3 (Low) |
| **Pre-Conditions** | Required state before test execution | Required | User state, system state, data state |
| **Test Steps** | Detailed, numbered execution steps | Required | Clear, sequential, actionable |
| **Test Data** | Specific data used in test | Required | Usernames, IDs, input values |
| **Expected Result** | Correct behavior per requirements | Required | Specific, measurable, verifiable |
| **Actual Result** | Observed outcome after execution | Fill during execution | Compare with expected result |
| **Status** | Test execution status | Fill during execution | Pass / Fail / Blocked / Not Run |

---

## Test Case Examples

### Example 1: Successful Registration (Happy Path)

| Field | Value |
|:------|:------|
| **Case ID** | SYS-REG-TC-001 |
| **Test Module** | User Registration |
| **Requirement ID** | SRS-USR-R1.1, SRS-USR-R1.5 |
| **Case Type** | Functional Testing (Positive) |
| **Title/Objective** | Successfully create new user with valid, unique credentials |
| **Priority** | P1 (High) |
| **Pre-Conditions** | 1. User is not logged in<br>2. Registration page is accessible<br>3. Email `test001@example.com` is not already registered |
| **Test Steps** | 1. Navigate to registration page<br>2. Enter username: `Tester001`<br>3. Enter email: `test001@example.com`<br>4. Enter password: `<VALID_PASSWORD>`<br>5. Enter confirm password: `<VALID_PASSWORD>`<br>6. Check "I agree to terms" checkbox<br>7. Click "Register" button |
| **Test Data** | Username: `Tester001`<br>Email: `test001@example.com`<br>Password: `<VALID_PASSWORD>`<br>Confirm Password: `<VALID_PASSWORD>` |
| **Expected Result** | 1. System displays "Registration successful" message<br>2. Page redirects to user dashboard or login page<br>3. New user record exists in database with encrypted password<br>4. Confirmation email sent to user |
| **Actual Result** | _(Fill during execution)_ |
| **Status** | Not Run |

---

### Example 2: Registration with Existing Email (Negative Path)

| Field | Value |
|:------|:------|
| **Case ID** | SYS-REG-TC-002 |
| **Test Module** | User Registration |
| **Requirement ID** | SRS-USR-R1.2 |
| **Case Type** | Functional Testing (Negative) |
| **Title/Objective** | Verify system prevents registration with already registered email |
| **Priority** | P1 (High) |
| **Pre-Conditions** | 1. User is not logged in<br>2. Registration page is accessible<br>3. Email `existing@example.com` is already registered in system |
| **Test Steps** | 1. Navigate to registration page<br>2. Enter username: `NewUser123`<br>3. Enter email: `existing@example.com`<br>4. Enter password: `<VALID_PASSWORD>`<br>5. Enter confirm password: `<VALID_PASSWORD>`<br>6. Check "I agree to terms" checkbox<br>7. Click "Register" button |
| **Test Data** | Username: `NewUser123`<br>Email: `existing@example.com` (already registered)<br>Password: `<VALID_PASSWORD>` |
| **Expected Result** | 1. System displays error: "Email already registered"<br>2. Registration is blocked<br>3. User remains on registration page<br>4. No duplicate user record created |
| **Actual Result** | _(Fill during execution)_ |
| **Status** | Not Run |

---

### Example 3: Registration with Weak Password (Boundary Test)

| Field | Value |
|:------|:------|
| **Case ID** | SYS-REG-TC-003 |
| **Test Module** | User Registration |
| **Requirement ID** | SRS-USR-R1.3 |
| **Case Type** | Functional Testing (Boundary) |
| **Title/Objective** | Verify password strength validation rejects weak passwords |
| **Priority** | P2 (Medium) |
| **Pre-Conditions** | 1. User is not logged in<br>2. Registration page is accessible<br>3. Password policy requires: 8+ chars, uppercase, lowercase, number, special char |
| **Test Steps** | 1. Navigate to registration page<br>2. Enter username: `TestUser456`<br>3. Enter email: `weak@example.com`<br>4. Enter password: `<WEAK_PASSWORD>` (weak password)<br>5. Enter confirm password: `<WEAK_PASSWORD>`<br>6. Attempt to check "I agree to terms"<br>7. Observe validation feedback |
| **Test Data** | Username: `TestUser456`<br>Email: `weak@example.com`<br>Password: `<WEAK_PASSWORD>` (fails complexity requirements) |
| **Expected Result** | 1. Password field shows validation error<br>2. Error message explains password requirements<br>3. "Register" button remains disabled or shows error<br>4. Registration is blocked |
| **Actual Result** | _(Fill during execution)_ |
| **Status** | Not Run |

---

## Test Case Design Guidelines

### Priority Classification

- **P1 (High)**: Core functionality, critical user flows, security features
- **P2 (Medium)**: Important features, common user scenarios
- **P3 (Low)**: Edge cases, nice-to-have features, cosmetic issues

### Test Coverage Types

Include diverse test case types:

1. **Positive/Happy Path**: Valid inputs, expected user behavior
2. **Negative**: Invalid inputs, error handling
3. **Boundary**: Min/max values, edge cases
4. **Security**: Authentication, authorization, injection attacks
5. **Performance**: Load times, response times under stress
6. **Integration**: Cross-module functionality

### Quality Checklist

Before finalizing test case report, verify:

- [ ] All test cases have unique Case IDs
- [ ] Each case links to specific requirement(s)
- [ ] Test steps are numbered and atomic
- [ ] Expected results are specific and measurable
- [ ] Test data includes all necessary values
- [ ] Priority is justified based on business impact
- [ ] Coverage includes positive, negative, and boundary cases

## Deliverable

**Output**: Detailed Test Case Report containing all test cases in standardized format, ready for execution phase.

## Next Steps

Once test case design is complete:
1. Review test cases for completeness and clarity
2. Confirm smoke tests passed successfully
3. Proceed to **Execution** phase to execute test cases systematically
