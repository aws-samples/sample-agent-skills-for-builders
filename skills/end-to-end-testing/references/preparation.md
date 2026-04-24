---
name: Preparation
description: Required inputs and configuration templates for test environment setup and test case documentation
---

# Preparation Phase

## Overview

Gather all necessary environment credentials and test case documentation before proceeding with test execution. This phase ensures you have proper access and clear testing objectives.

## Required Inputs

### 1. Test Environment Configuration

Users must provide environment information in the following format:

```bash
# .test.env

# AWS CLI Configuration
AWS_PROFILE=test
AWS_REGION=us-east-1

# CloudFormation Stack
STACK_NAME=my-application-stack

# Application Portal
PORTAL_URL=https://test.example.com

# Test User Credentials
USER=testuser@example.com
PASSWORD=Sec0reP@ss1
```

**Validation Checklist**:
- [ ] AWS credentials are valid (test with `aws sts get-caller-identity`)
- [ ] CloudFormation stack exists and is in stable state
- [ ] Portal URL is accessible
- [ ] Test user credentials are confirmed working

---

### 2. Test Case Suite

Users must provide test cases in structured format. Below is the standard template and an example.

#### Test Case Template

```markdown
# Case [N]: [Test Case Title]

## Pre-Conditions
- [Condition 1: State that must exist before testing]
- [Condition 2: Required setup or configuration]

## Test Steps
1. [Action 1: First step to perform]
2. [Action 2: Second step to perform]
3. [Action 3: Third step to perform]

## Test Data
- [Data Field 1]: [Specific value to use]
- [Data Field 2]: [Specific value to use]

## Expected Result
- [Expected Outcome 1: What should happen]
- [Expected Outcome 2: Additional expected behavior]
```

---

#### Example: Successful Login Test Case

```markdown
# Case 1: Successful Login with Valid Credentials

## Pre-Conditions
- User has completed registration and is not currently logged in
- Login page is accessible

## Test Steps
1. Navigate to the login page
2. Enter username in the username field
3. Enter password in the password field
4. Click the "Login" button

## Test Data
- Username: user@example.com
- Password: Sec0reP@ss1

## Expected Result
- Login succeeds without errors
- Page automatically redirects to the home dashboard
- User session is established (verify cookie/token)
```

---

## Input Validation

Before proceeding to Planning & Design phase, confirm:

1. **Environment Access**
   - AWS CLI commands execute successfully
   - Portal URL responds (HTTP 200)
   - Stack resources are deployed

2. **Test Case Completeness**
   - Each test case has all required sections
   - Pre-conditions are clearly stated
   - Test steps are atomic and sequential
   - Expected results are specific and verifiable

3. **Credentials Security**
   - Test credentials are for non-production environments
   - Sensitive data is properly protected
   - Access permissions are appropriate for testing

## Common Issues

| Issue | Solution |
|:------|:---------|
| AWS credentials expired | Refresh credentials using SSO or IAM |
| Portal URL not accessible | Verify VPN connection, security groups, DNS |
| Stack not found | Confirm stack name and region are correct |
| Test cases lack detail | Request clarification on steps and expected results |

## Next Steps

Once all inputs are validated:
1. Store environment configuration securely
2. Review test cases for completeness
3. Proceed to **Planning & Design** phase for smoke testing and detailed test case design
