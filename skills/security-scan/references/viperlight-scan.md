# Viperlight 安全扫描

## 目标

使用 Viperlight 扫描代码中的敏感信息、密钥泄露、安全漏洞。

## 前置条件

- 已安装 Viperlight CLI（安装参考: https://w.amazon.com/bin/view/AWS/Teams/GlobalServicesSecurity/Tools/Viperlight/）

## 执行步骤

### Step 1: 获取扫描目录并确认工具

```bash
source security-scan-results/.current-scan
viperlight --version
```

### Step 2: 检查配置文件

确保项目根目录有以下配置文件：

**`.viperlightrc`** - 如不存在则创建：
```json
{"failOn":"low","all":true}
```

**`.viperlightignore`** - 常见忽略目录：
```
.github/
cdk.out/*
node_modules/
coverage/
.*/package-lock.json
public/*
.next/
dist/
build/
*.lock
```

### Step 3: 确定扫描目标目录

**必须使用 `--target` 指定核心源代码目录**，不要扫描整个项目。

首先确定项目的源代码目录（按优先级检查）：

```bash
# 常见源代码目录，按优先级检查
SCAN_TARGETS=""

# 检查常见目录是否存在（使用 PROJECT_ROOT 绝对路径）
for dir in src lib lambda functions app packages; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        SCAN_TARGETS="$SCAN_TARGETS $PROJECT_ROOT/$dir/"
    fi
done

# 如果没有找到常见目录，扫描项目根目录
if [ -z "$SCAN_TARGETS" ]; then
    SCAN_TARGETS="$PROJECT_ROOT"
fi

echo "扫描目标目录: $SCAN_TARGETS"
```

**示例**: 对于典型 CDK 项目，扫描目标可能是 `src/infrastructure/ src/portal/`

### Step 4: 执行扫描

首次执行时保存为 `output_origin.txt`，后续修复重试时覆盖 `output.txt`：

```bash
# 首次执行：保存原始输出
if [ ! -f "${SCAN_DIR}/03-viperlight/output_origin.txt" ]; then
    viperlight scan --target $SCAN_TARGETS > "${SCAN_DIR}/03-viperlight/output_origin.txt" 2>&1
    cp "${SCAN_DIR}/03-viperlight/output_origin.txt" "${SCAN_DIR}/03-viperlight/output.txt"
else
    # 修复后重试：覆盖 output.txt
    viperlight scan --target $SCAN_TARGETS > "${SCAN_DIR}/03-viperlight/output.txt" 2>&1
fi
```

### Step 5: 检查状态并修复

```bash
grep -E "Status:" "${SCAN_DIR}/03-viperlight/output.txt"
```

- `Status: PASSED` → 扫描通过，跳到 Step 5
- `Status: FAILED` → 必须修复所有问题直到 PASSED

**⚠️ 修复原则**：代码修复优先，只有在确认是误报或无法修复时**，才使用 `# nosec` 注释

**常见问题修复方式**：

| 问题类型 | 修复方式 |
|---------|---------|
| 硬编码密钥/密码 | 移除并使用环境变量或 Secrets Manager |
| AWS Access Key | 立即轮换，从代码移除，使用 IAM Role |
| 私钥文件 | 移出仓库，添加到 `.gitignore` |
| `try_except_pass` (B110) | 改为 `except Exception as e: print(f"Warning: {e}")` |
| `subprocess` (B603/B404) | 确认输入可信后添加 `# nosec B603` 注释 |

**注意**: `# nosec` 必须在同一行末尾，并附带理由说明。

修复后重新扫描直到 PASSED（会覆盖 `output.txt`，保留 `output_origin.txt`）：
```bash
viperlight scan --target $SCAN_TARGETS > "${SCAN_DIR}/03-viperlight/output.txt" 2>&1
```

### Step 6: 生成结果文件

```bash
echo "$ viperlight scan --target $SCAN_TARGETS" > "${SCAN_DIR}/result/viperlight.txt"
echo '' >> "${SCAN_DIR}/result/viperlight.txt"
sed 's/\x1b\[[0-9;]*m//g' "${SCAN_DIR}/03-viperlight/output.txt" >> "${SCAN_DIR}/result/viperlight.txt"
```

### Step 7: 生成修复报告（如有修复）

如果进行了代码修复，创建 `${SCAN_DIR}/03-viperlight/fix-report.md`，记录：
- 发现的问题（文件位置、问题描述）
- 修复方案（diff 格式）
- 验证结果

## 输出文件说明

| 文件 | 说明 |
|------|------|
| `output_origin.txt` | 首次执行的原始输出（保留不变，记录原始问题） |
| `output.txt` | 最新执行的输出（修复后会覆盖，记录最终状态） |

## 完成标志

- [ ] `${SCAN_DIR}/result/viperlight.txt` 存在且包含 `Status: PASSED`
- [ ] 如有修复，`fix-report.md` 已创建

**记录用时**:
```bash
echo "STEP_03_END=$(date +%s)" >> security-scan-results/.current-scan
```

## 下一步

完成后继续执行 [04-license-check.md](04-license-check.md)
