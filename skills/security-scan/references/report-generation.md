# 生成扫描汇总报告

## 目标

汇总所有扫描结果，生成最终报告供提交。

## 执行步骤

### Step 1: 获取扫描目录和时间信息

```bash
source security-scan-results/.current-scan
echo "扫描目录: ${SCAN_DIR}"
```

### Step 2: 计算各步骤用时

读取 `.current-scan` 中的时间戳，计算每步用时：

```bash
# 格式化时间函数（秒数转为 Xm Ys 格式）
format_duration() {
    local seconds=$1
    if [ $seconds -ge 60 ]; then
        local mins=$((seconds / 60))
        local secs=$((seconds % 60))
        echo "${mins}m ${secs}s"
    else
        echo "${seconds}s"
    fi
}

# 计算各步骤用时
STEP_01_DURATION=$((STEP_01_END - SCAN_START_TIME))
STEP_02_DURATION=$((STEP_02_END - STEP_01_END))
STEP_03_DURATION=$((STEP_03_END - STEP_02_END))
STEP_04_DURATION=$((STEP_04_END - STEP_03_END))
STEP_05_DURATION=$((STEP_05_END - STEP_04_END))
STEP_06_DURATION=$((STEP_06_END - STEP_05_END))
STEP_07_DURATION=$((STEP_07_END - STEP_06_END))

# 总用时
TOTAL_DURATION=$((STEP_07_END - SCAN_START_TIME))
```

### Step 3: 确认所有扫描文件存在

```bash
ls -la "${SCAN_DIR}/"
```

应包含以下目录：
- `01-architecture/`
- `02-cdk-synth/`
- `03-viperlight/`
- `04-license/`
- `05-trivy/`
- `06-ash/`
- `07-deploy/`

### Step 4: 生成汇总报告

创建 `${SCAN_DIR}/SUMMARY.md`，包含用时统计：

```markdown
# Security Scan Summary Report

## 扫描信息

| 项目 | 值 |
|------|-----|
| 扫描时间 | [扫描开始时间] |
| 项目名称 | [项目名称] |
| 分支 | [git branch] |
| Commit | [git commit hash] |
| 扫描目录 | ${SCAN_DIR} |
| **总用时** | **[总用时，如 1h 23m 45s]** |

## 各步骤用时

| 步骤 | 扫描类型 | 用时 | 状态 |
|------|---------|------|------|
| 01 | Architecture | [用时] | ✅/❌ |
| 02 | CDK Synth | [用时] | ✅/❌ |
| 03 | Viperlight | [用时] | ✅/❌ |
| 04 | License | [用时] | ✅/❌ |
| 05 | Trivy | [用时] | ✅/❌ |
| 06 | ASH | [用时] | ✅/❌ |
| 07 | Deploy | [用时] | ✅/❌ |

## 扫描结果概览

| 扫描类型 | 状态 | 修复数 | 跳过数 | 说明 |
|---------|------|-------|-------|------|
| CDK Synth | ✅/❌ | 0 | 0 | [说明] |
| Viperlight | ✅/❌ | 0 | 0 | [说明] |
| ASH | ✅/❌ | 0 | 0 | [说明] |
| Trivy | ✅/❌ | 0 | 0 | [说明] |
| Architecture | ✅/❌ | - | - | [说明] |
| License | ✅/❌ | - | - | [说明] |
| Deploy | ✅/❌ | 0 | 0 | [说明] |

## 修复记录汇总
...
```

**用时格式说明**：
- 小于 60 秒：显示为 `45s`
- 60 秒以上：显示为 `1m 23s`
- 60 分钟以上：显示为 `1h 23m 45s`

### Step 5: 更新汇总报告

根据实际扫描结果，编辑 `${SCAN_DIR}/SUMMARY.md`：
1. 填写每个扫描的实际状态
2. 统计各步骤的修复数量
3. 记录豁免的问题及原因
4. 确认文件清单完整

## 完成标志

- [ ] `SUMMARY.md` 已创建并填写完整
- [ ] **各步骤用时已计算并填充**（从 `.current-scan` 读取 `STEP_0X_END` 计算，非占位符）
- [ ] 所有扫描文件已确认存在
- [ ] 报告已准备好提交

---

# 生成 HTML 汇总报告

## 目标

将所有扫描结果整合到一个单独的 HTML 文件中，使用现代化的 Tab 导航界面，方便查看和分享。

## 执行步骤

### Step 1: 获取扫描目录

```bash
source security-scan-results/.current-scan
echo "扫描目录: ${SCAN_DIR}"
```

### Step 2: 确认所有结果文件存在

```bash
ls -la "${SCAN_DIR}/result/"
ls -la "${SCAN_DIR}/result/ash/"
```

应包含以下文件：
- `SUMMARY.md` - 汇总报告
- `result/architecture.png` - 架构图
- `result/cdk-synth.txt` - CDK 模板
- `result/viperlight.txt` - Viperlight 扫描结果
- `result/license.md` - 许可证报告
- `result/trivy.md` - Trivy 扫描摘要
- `result/ash/ash.md` - ASH 报告 (Markdown)
- `result/ash/ash.html` - ASH 报告 (HTML)
- `result/ash/ash.yaml` - ASH 配置
- `07-deploy/output.txt` - 部署日志

### Step 3: 使用脚本生成 HTML 报告

**重要**: 使用独立的 Python 脚本自动生成 HTML 报告。脚本位于 skill 目录的 `scripts/` 子目录中。

```bash
# 获取 skill 目录路径（假设 skill 安装在 .claude/skills/security-scan/ 下）
SKILL_DIR="${HOME}/.claude/skills/security-scan"

# 如果是项目级 skill，使用相对路径
if [ -f ".claude/skills/security-scan/scripts/generate-html-report.py" ]; then
    SKILL_DIR=".claude/skills/security-scan"
fi

python3 "${SKILL_DIR}/scripts/generate-html-report.py" "${SCAN_DIR}"
```

脚本会自动：
1. 读取所有扫描结果文件
2. 将架构图转换为 base64 嵌入
3. 生成带有 Tab 导航的现代化 HTML 报告
4. 输出到 `${SCAN_DIR}/report.html`

### Step 4: 验证生成的报告

```bash
ls -la "${SCAN_DIR}/report.html"
```

### Step 5: 记录用时

```bash
echo "STEP_09_END=$(date +%s)" >> security-scan-results/.current-scan
```

## 完成标志

- [ ] `${SCAN_DIR}/report.html` 已生成

## 下一步

**无 - 这是最后一步**

扫描流程已全部完成，`report.html` 是最终的汇总报告，可以直接打开查看所有扫描结果。

---

## 扫描完成

恭喜！安全扫描流程已全部完成。

最终报告文件：`${SCAN_DIR}/report.html`

可以直接在浏览器中打开查看所有扫描结果。
