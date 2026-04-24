# 部署验证

## 🚫 禁止跳过此步骤

**绝对禁止以任何理由跳过此步骤！**

- ❌ 禁止因 "之前扫描有问题" 而跳过 → 必须执行部署
- ❌ 禁止因 "Stack 已存在" 而跳过 → 必须重新执行 `cdk deploy`
- ❌ 禁止因 "时间限制" 而跳过 → 必须等待部署完成
- ❌ 禁止仅检查 Stack 状态就跳过 → 必须实际执行部署命令
- ❌ 禁止创建 skipped.txt 文件 → 必须执行实际部署

**如果部署失败，必须排查原因、修复代码后重新部署，直到成功为止。**

## 目标

验证当前代码能够成功部署到 AWS。

## 前置条件

- 所有前置扫描已完成
- 所有 CRITICAL/HIGH 问题已修复
- 已完成前置准备 (确认 Region 和 Email)

## 执行步骤

### Step 1: 获取扫描配置并设置 Region

```bash
source security-scan-results/.current-scan
export AWS_REGION=${SCAN_REGION}  # 设置部署目标 Region
echo "Region: ${SCAN_REGION}"
echo "Email: ${SCAN_EMAIL}"
```

### Step 1.5: 检查 ACM 证书

阅读项目 README 或 install 脚本，确认部署是否需要 ACM 证书参数。

**如需证书**：
1. 检查现有证书：`aws acm list-certificates --region ${SCAN_REGION}`
2. 若无可用证书，按项目文档在当前 region 创建一个新的 ACM 证书
3. 保存到配置：`echo "ACM_CERT_ARN=<arn>" >> security-scan-results/.current-scan`，部署时使用

**如不需要证书**：直接执行 Step 2

### Step 2: 执行部署

**⚠️ 重要：禁止使用交互式命令！**

通常 `install.sh` 脚本包含交互式 `read` 命令获取 email，必须直接使用 `npx cdk deploy` 命令：

```bash
# 直接使用 cdk deploy，具体参数请参考 readme 或者 install.sh 等安装脚本中的定义。禁止使用 install.sh 的交互式输入, 如下为一个示例：
npx cdk deploy --all --context Email=${SCAN_EMAIL} --require-approval never
```

**部署方式**:
1. **全新部署**: 如果没有现有 Stack，执行上述命令
2. **更新部署**: 如果有现有 Stack，同样执行上述命令进行更新

**重要**:
- 使用 `.current-scan` 中记录的 `SCAN_EMAIL` 和 `SCAN_REGION`
- 必须等待部署完成，不能中途跳过

### Step 3: 验证部署成功

**部署成功的必要条件** (全部满足才算成功):

1. ✅ 部署输出的 Outputs 内容不为空
2. ✅ Stack 状态为 `CREATE_COMPLETE` 或 `UPDATE_COMPLETE`

验证 Stack 状态:
```bash
aws cloudformation describe-stacks --stack-name <STACK_NAME> \
  --query "Stacks[0].StackStatus" --output text
```

只有看到以上所有标志,才算部署成功。

**重要提示Important !!!**: 如果部署失败，请查找失败原因, 修复代码后重新部署, 直到成功为止。

## 常见问题

**Stack 回滚**: 检查 CloudFormation 事件日志, 修复问题后重新部署。
**ARM架构兼容问题导致部署失败**: 请实现多架构兼容部署，需要在x86，ARM 机器上都能正确部署。

### BedrockAgentCore ARM64 限制

改用 `docker buildx` 构建 ARM64 镜像。

## 完成标志

- [ ] **已执行 `cdk deploy` 命令**（不能仅检查stack之前的状态）
- [ ] 部署需要全部成功，不允许部分成功就跳过
- [ ] Stack 状态为 CREATE_COMPLETE 或 UPDATE_COMPLETE
- [ ] 生成 deploy-report.md

**记录用时**:
```bash
echo "STEP_07_END=$(date +%s)" >> security-scan-results/.current-scan
```

## 下一步

检查完成标志，所有内容检查通过后，再继续执行 [08-generate-summary.md](08-generate-summary.md)
