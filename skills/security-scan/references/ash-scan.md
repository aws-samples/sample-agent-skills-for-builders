# ASH (Automated Security Helper) 扫描

## 🚫 禁止跳过此步骤

**绝对禁止以任何理由跳过此步骤！**

- ❌ 禁止因 "ASH 未安装" 而跳过 → 必须先安装再执行
- ❌ 禁止因 "扫描时间长" 而跳过 → 必须等待完成（15-30分钟是正常的）
- ❌ 禁止因 "Docker 镜像构建失败" 而跳过 → 必须排查并解决
- ❌ 禁止创建 skipped.txt 文件 → 必须执行实际扫描

**如果遇到问题，必须解决问题后继续执行，而不是跳过。**

## 目标

使用 ASH 工具扫描 AWS 安全最佳实践合规性。

## 前置条件

### 条件 1: 检查基础环境依赖

- Python 3.10+
- Docker（必须运行中）
- uv (Python package manager)

### 条件 2: 安装 ASH

```bash
# Install uv if you don't have it
curl -sSf https://astral.sh/uv/install.sh | sh

# Create an alias for ASH (使用固定版本 v3.1.5 避免构建问题)
alias ash='uvx --from "git+https://github.com/awslabs/automated-security-helper.git@v3.1.5" ash'
```

**重要：必须使用 Docker 模式**

ASH 扫描必须使用 `--mode container`，禁止使用 `--mode local`。原因：
- Container 模式将所有扫描工具打包在 Docker 镜像中，无需本地安装
- Local 模式需要手动安装 bandit、checkov、semgrep、grype 等多个工具
- Container 模式保证环境一致性，避免本地环境差异导致的问题

执行前请确认：
```bash
# 确认 Docker 正在运行
docker info > /dev/null 2>&1 && echo "Docker is running" || echo "Docker is NOT running"
```

### Docker 镜像构建问题处理

如果首次运行 ASH 时 Docker 镜像构建失败（如 `uv build` 错误），可以尝试以下方法：

1. **清理并重试**：
   ```bash
   docker rmi automated-security-helper:non-root
   ash --mode container --output-dir output/
   ```

**注意**：遇到问题时必须解决问题，不能切换到 local 模式，不能使用已有镜像。

## 重要规则

1. **先清理再扫描**：扫描前删除 `node_modules` 和 `cdk.out` 目录，避免扫描大量第三方文件
2. **先初始化再配置再扫描**：`ash config init` → 配置 suppressions → 运行扫描
3. **代码修复优先**：能通过代码修复的问题必须修复，无法修复的误报才添加到 suppressions
4. **修复-重扫循环**：发现问题后修复或更新配置，重新扫描直到通过
5. **结果归档**：扫描通过后，将配置和结果文件拷贝到 result 目录

## 输出目录结构

```
06-ash/
├── output/                      # ASH 扫描输出目录
│   ├── reports/
│   │   ├── ash.html
│   │   ├── ash.summary.md
│   │   └── ...
│   └── ash_aggregated_results.json
└── fix-report.md                # 修复报告（如有）

# 扫描通过后归档到：
result/ash/
├── ash.yaml                     # 配置文件副本
├── ash.md                       # 扫描摘要报告
└── ash.html
```

## 执行步骤

### Step 1: 获取扫描目录

```bash
source security-scan-results/.current-scan
mkdir -p "${SCAN_DIR}/06-ash"
```

### Step 2: 清理第三方依赖和构建输出目录

删除 `node_modules`、`cdk.out` 和 `.next` 目录，避免扫描大量第三方文件和构建产物（扫描后可通过 `pnpm install` 恢复）：

```bash
# 删除所有 node_modules 目录
find "$PROJECT_ROOT" -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null

# 删除 cdk.out 目录
rm -rf "$PROJECT_ROOT/cdk.out"

# 删除所有 .next 目录（Next.js 构建输出）
find "$PROJECT_ROOT" -name ".next" -type d -prune -exec rm -rf {} + 2>/dev/null
```

### Step 3: 确认 ASH 已安装

```bash
# 使用固定版本运行
uvx --from "git+https://github.com/awslabs/automated-security-helper.git@v3.1.5" ash --version
```

### Step 4: 初始化并配置 ASH

```bash
ash config init
```

编辑生成的 `.ash/.ash.yaml`。

**⚠️ 配置文件格式要求：**

1. `fail_on_findings` 必须在**顶层**，不能放在 `global_settings` 里
2. suppressions 的 `path` 必须使用**完整路径**，不支持通配符 `**`
3. 每个需要 suppress 的文件都要单独添加一条规则

**正确的配置文件格式：**

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/awslabs/automated-security-helper/refs/heads/main/automated_security_helper/schemas/AshConfig.json
project_name: your-project-name
fail_on_findings: true  # 必须在顶层！

global_settings:
  severity_threshold: MEDIUM
  ignore_paths:
    - path: 'node_modules/'
      reason: 'Third-party dependencies'
    - path: 'cdk.out/'
      reason: 'CDK build output'
    - path: '.next/'
      reason: 'Next.js build output'
  suppressions:
    # 每个文件单独添加规则，使用完整路径
    - rule_id: 'CKV_DOCKER_2'
      path: 'src/infrastructure/lambda/my-function/Dockerfile'
      reason: 'Lambda containers do not need HEALTHCHECK'

ash_plugin_modules: []
```

**❌ 错误示例（不要这样写）：**

```yaml
global_settings:
  fail_on_findings: true  # 错误！不能放在 global_settings 里
  suppressions:
    - rule_id: 'CKV_DOCKER_2'
      path: 'src/infrastructure/**'  # 错误！不支持通配符
```

### Step 5: 执行 ASH 扫描

**必须使用 `ASH_CONFIG` 环境变量指定配置文件：**

```bash
export ASH_CONFIG=".ash/.ash.yaml"
ash --mode container --output-dir "${SCAN_DIR}/06-ash/output" 2>&1 | tee "${SCAN_DIR}/06-ash/scan-log.txt"
```

### Step 6: 分析并修复问题

检查 `${SCAN_DIR}/06-ash/output/reports/` 下的报告（推荐查看 `ash.html` 或 `ash.summary.md`）。

**处理原则**：
- **能修复的问题** → 修改代码
- **确认是误报** → 添加到 `.ash/.ash.yaml` 的 suppressions

#### 常见可修复问题

| 问题 | 修复方案 |
|------|---------|
| IAM 权限过宽 (`*` resource) | 限制到具体 ARN |
| S3 未加密 | 添加 `encryption: s3.BucketEncryption.S3_MANAGED` |
| S3 公开访问 | 添加 `blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL` |
| 安全组 0.0.0.0/0 | 限制到 VPC CIDR |

#### Suppressions 添加原则

**重要：不要预先添加 suppressions！** 只有在扫描发现问题后，经过分析确认是误报，才添加对应的 suppression。

添加 suppression 的流程：
1. 运行扫描，查看报告中的具体问题
2. 分析每个问题，判断是真实问题还是误报
3. 真实问题 → 修复代码
4. 确认是误报 → 添加 suppression 并记录理由

#### Lambda/ECS Dockerfile 常见误报

对于 Lambda 和 ECS 容器的 Dockerfile，以下检查通常是误报：

| Rule ID | 说明 | Reason |
|---------|------|--------|
| `CKV_DOCKER_2` | HEALTHCHECK 检查 | Lambda/ECS 容器由 AWS 管理生命周期，不需要 Docker HEALTHCHECK |
| `CKV_DOCKER_3` | USER 检查 | Lambda 容器应使用默认用户以获得正确的文件系统权限 |
| `dockerfile.security.missing-user.missing-user` | 同上 | 同上 |

**⚠️ 必须为每个 Dockerfile 单独添加 suppression 规则：**

```yaml
global_settings:
  suppressions:
    # Lambda Dockerfile 1
    - rule_id: 'CKV_DOCKER_2'
      path: 'src/infrastructure/lambda/function-a/Dockerfile'
      reason: 'Lambda containers do not need HEALTHCHECK - AWS Lambda manages container lifecycle'
    - rule_id: 'CKV_DOCKER_3'
      path: 'src/infrastructure/lambda/function-a/Dockerfile'
      reason: 'Lambda containers should use default user for proper file system permissions'
    - rule_id: 'dockerfile.security.missing-user.missing-user'
      path: 'src/infrastructure/lambda/function-a/Dockerfile'
      reason: 'Lambda containers should use default user for proper file system permissions'

    # Lambda Dockerfile 2
    - rule_id: 'CKV_DOCKER_2'
      path: 'src/infrastructure/lambda/function-b/Dockerfile'
      reason: 'Lambda containers do not need HEALTHCHECK - AWS Lambda manages container lifecycle'
    # ... 为每个 Dockerfile 重复添加
```

### Step 7: 重新扫描验证

修复后重新扫描，重复 Step 5-6 直到无 CRITICAL/HIGH 问题：

```bash
export ASH_CONFIG=".ash/.ash.yaml"
ash --mode container --output-dir "${SCAN_DIR}/06-ash/output"
```

### Step 8: 归档结果

```bash
mkdir -p "${SCAN_DIR}/result/ash"
cp .ash/.ash.yaml "${SCAN_DIR}/result/ash/ash.yaml"
cp "${SCAN_DIR}/06-ash/output/reports/ash.html" "${SCAN_DIR}/result/ash/" 2>/dev/null || true
```

### Step 9: 生成结果报告

生成 `${SCAN_DIR}/result/ash/ash.md`，包含：
1. 扫描摘要（通过/失败状态）
2. .ash.yaml 中 suppressions 列表的所有内容和对应的理由
3. 包含 fix-report.md 中的所有改动说明（如有）

## 完成标志

- [ ] `.ash/.ash.yaml` 配置文件已创建
- [ ] `${SCAN_DIR}/06-ash/output/` 目录存在
- [ ] 无 CRITICAL 级别问题
- [ ] 无 HIGH 级别问题（或已添加 suppression 并记录理由）
- [ ] `${SCAN_DIR}/result/ash/` 目录已创建
- [ ] `${SCAN_DIR}/result/ash/ash.md` 已生成
- [ ] `${SCAN_DIR}/result/ash/ash.md` 包含 "Suppressions 配置" 章节（列出所有 suppressions 及理由）
- [ ] `${SCAN_DIR}/result/ash/ash.yaml` 已生成
- [ ] `${SCAN_DIR}/result/ash/ash.html` 已生成
- [ ] 如有修复，`fix-report.md` 已更新

**记录用时**:
```bash
echo "STEP_06_END=$(date +%s)" >> security-scan-results/.current-scan
```

## 下一步

完成后继续执行 [07-deploy-verify.md](07-deploy-verify.md)
