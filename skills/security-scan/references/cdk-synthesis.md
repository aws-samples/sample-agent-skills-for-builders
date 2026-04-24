# CDK Synth 扫描

## 目标

生成 CDK CloudFormation 模板，验证 CDK 代码能正确合成。

## 前置条件

- Node.js 和 pnpm/npm
- AWS CDK CLI (`npm install -g aws-cdk`)
- Docker（用于构建 Python Lambda）

## 执行步骤

### Step 1: 获取扫描目录

```bash
source security-scan-results/.current-scan
```

### Step 2: 登录 ECR Public

```bash
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

**注意**: 必须使用 `us-east-1`，与项目部署 region 无关。

### Step 3: 安装依赖

根据项目使用的包管理器安装依赖。

**⚠️ pnpm 10+**: 如遇 `approve-builds` 提示，需先在 `package.json` 中添加 `pnpm.onlyBuiltDependencies` 配置以确保非交互式执行。

```bash
# 检测并使用正确的包管理器
if [ -f "pnpm-lock.yaml" ]; then
    pnpm install
elif [ -f "yarn.lock" ]; then
    yarn install
elif [ -f "package-lock.json" ]; then
    npm install
else
    npm install
fi
```

### Step 4: 执行 CDK Synth

首次执行时保存为 `output_origin.txt`，后续修复重试时覆盖 `output.txt`：

```bash
# 首次执行：保存原始输出
if [ ! -f "${SCAN_DIR}/02-cdk-synth/output_origin.txt" ]; then
    npx cdk synth 2>&1 | tee "${SCAN_DIR}/02-cdk-synth/output_origin.txt"
else
    # 修复后重试：覆盖 output.txt
    npx cdk synth 2>&1 | tee "${SCAN_DIR}/02-cdk-synth/output.txt"
fi
```

### Step 5: 提取 CloudFormation 模板

根据是否存在 `output.txt` 选择输出源：

```bash
# 如果有修复后的 output.txt 则用它，否则用原始输出
if [ -f "${SCAN_DIR}/02-cdk-synth/output.txt" ]; then
    OUTPUT_FILE="${SCAN_DIR}/02-cdk-synth/output.txt"
else
    OUTPUT_FILE="${SCAN_DIR}/02-cdk-synth/output_origin.txt"
fi

# 提取从 Metadata: 开始的内容（trim 前导空格后匹配）
awk '{line=$0; gsub(/^[[:space:]]+/, "", line)} line ~ /^Metadata:/ {found=1} found' "${OUTPUT_FILE}" > "${SCAN_DIR}/result/cdk-synth.txt"
```

### Step 6: 检查结果

- **成功**: `cdk-synth.txt` 存在且以 `Metadata:` 开头
- **失败**: 输出文件包含 `Error`、`Exception`、`failed`

**常见错误**:

| 错误 | 修复 |
|------|------|
| ECR Public 403 | Step 1 登录 + `docker buildx prune -f` |
| Cannot find module | 重新安装依赖 |
| Cannot retrieve context | `cdk context --clear` |
| Missing context | 检查 README 中的部署参数要求 |

## 输出文件说明

| 文件 | 说明 |
|------|------|
| `output_origin.txt` | 首次执行的原始输出（保留不变） |
| `output.txt` | 最新执行的输出（修复后会覆盖） |

## 完成标志

- [ ] `output_origin.txt` 或者 `output.txt` 无错误
- [ ] `cdk-synth.txt` 存在且内容有效
- [ ] 如有修复，创建 `fix-report.md`

**记录用时**:
```bash
echo "STEP_02_END=$(date +%s)" >> security-scan-results/.current-scan
```

## 下一步

继续执行 [03-viperlight-scan.md](03-viperlight-scan.md)
