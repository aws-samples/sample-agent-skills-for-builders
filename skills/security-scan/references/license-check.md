# License 许可证检查

## 目标

扫描项目中所有语言的第三方依赖库许可证，生成合规性报告，识别潜在风险许可证。

## 预批准许可证列表 (Amazon Open Source Policy)

### ✅ 低风险 (可自由使用)
| 许可证 | 变体 |
|--------|------|
| Apache-2.0 | ImageMagick |
| BSD | Apache-1.1, BSD-3-Clause, BSD-2-Clause, BSD-2-Clause-FreeBSD, BSD-3-Clause-Attribution, BSD-1-Clause, BSD-Source-Code, 0BSD, EDL, OLDAP-2.8 |
| MIT | MIT-0, ISC, X11, BouncyCastle, Boost, PostgreSQL, PIL, curl, NTP, HPND, HPND-sell-variant, metamail |
| Zlib | zlib-acknowledgement, libpng, bzip2, Spencer-94 |
| Python-2.0 / PSF-2.0 | Python-2.1.1 |
| 其他 | OpenSSL, JSON, libjpeg, WTFPL, Unicode-*, CC0-1.0, Unlicense, CC-BY-*, Ruby, BlueOak-1.0.0, SIL-OFL-1.1, HDF5 |

### ⚠️ 中风险 (未修改包可批准)
| 许可证 | 说明 |
|--------|------|
| MPL-2.0 | Mozilla Public License - 修改的文件需开源 |
| CDDL-1.0/1.1 | Common Development and Distribution License |
| EPL-2.0 | Eclipse Public License |

### ❌ 高风险 (需法务审查)
| 许可证 | 说明 |
|--------|------|
| GPL-*, AGPL-*, LGPL-* | Copyleft 许可证 |
| CC-BY-NC-* | 非商业限制 |
| UNKNOWN / UNLICENSED | 未知许可证 |

## 执行步骤

### Step 1: 获取扫描目录

```bash
source security-scan-results/.current-scan
mkdir -p "${SCAN_DIR}/04-license"
```

### Step 2: 扫描 Node.js 依赖

**重要**: 必须扫描 `nodejs-dirs.txt` 中列出的所有目录，确保每个包含 `node_modules` 的目录都被单独扫描并生成对应的 CSV 文件。

```bash
find "$PROJECT_ROOT" -name "package.json" -not -path "*/node_modules/*" -not -path "*/cdk.out/*" > "${SCAN_DIR}/04-license/nodejs-dirs.txt"

cat "${SCAN_DIR}/04-license/nodejs-dirs.txt" | while read pkg; do
  dir=$(dirname "$pkg")
  name=$(echo "$dir" | tr '/' '-' | sed 's/^.-//')
  [ "$dir" = "." ] && name="root"

  if [ -d "${dir}/node_modules" ]; then
    echo "Scanning ${dir}..."
    npx license-checker --start "$dir" --csv > "${SCAN_DIR}/04-license/nodejs-${name}.csv" 2>/dev/null
  fi
done
```

**验证要求**:
- 检查 `nodejs-dirs.txt` 中的每个目录
- 对于有 `node_modules` 的目录，确认生成了对应的 `nodejs-*.csv` 文件
- 记录哪些目录被扫描、哪些目录因无 `node_modules` 而跳过

### Step 3: 扫描 Python 依赖

**重要**: 必须扫描 `python-dirs.txt` 中列出的所有 `requirements.txt` 文件，确保所有 Python 依赖都被安装并扫描。

```bash
find "$PROJECT_ROOT" -name "requirements.txt" -not -path "*/node_modules/*" -not -path "*/cdk.out/*" > "${SCAN_DIR}/04-license/python-dirs.txt"

python3 -m venv /tmp/license-scan-venv
source /tmp/license-scan-venv/bin/activate
pip install pip-licenses -q

cat "${SCAN_DIR}/04-license/python-dirs.txt" | while read req; do
  echo "Installing dependencies from: $req"
  pip install -r "$req" -q 2>/dev/null || true
done

pip-licenses --format=csv --with-urls > "${SCAN_DIR}/04-license/python.csv"

deactivate
rm -rf /tmp/license-scan-venv
```

**验证要求**:
- 检查 `python-dirs.txt` 中的每个 `requirements.txt` 文件
- 确认所有文件中的依赖都被安装到虚拟环境
- 确认 `python.csv` 包含所有 Python 依赖的许可证信息

### Step 3.1: 扫描 C# 依赖 (可选)

如果项目包含 `.csproj` 文件，执行 C# 依赖扫描：

```bash
# 检查是否有 C# 项目
CSPROJ_COUNT=$(find "$PROJECT_ROOT" -name "*.csproj" -not -path "*/node_modules/*" -not -path "*/cdk.out/*" 2>/dev/null | wc -l)

if [ "$CSPROJ_COUNT" -gt 0 ]; then
  echo "Found $CSPROJ_COUNT C# projects, scanning..."

  # 安装工具 (如未安装)
  dotnet tool install --global nuget-license 2>/dev/null || true

  # 扫描并生成 CSV
  nuget-license --input . --output-type csv > "${SCAN_DIR}/04-license/csharp.csv" 2>/dev/null || true

  echo "C# license scan completed"
else
  echo "No C# projects found, skipping..."
fi
```

### Step 4: 使用脚本生成报告

**重要**: 使用独立的 Python 脚本自动生成报告。脚本位于 skill 目录的 `scripts/` 子目录中。

```bash
# 获取 skill 目录路径（假设 skill 安装在 .claude/skills/pcsr-scan/ 下）
SKILL_DIR="${HOME}/.claude/skills/pcsr-scan"

# 如果是项目级 skill，使用相对路径
if [ -f ".claude/skills/pcsr-scan/scripts/generate-license-report.py" ]; then
    SKILL_DIR=".claude/skills/pcsr-scan"
fi

python3 "${SKILL_DIR}/scripts/generate-license-report.py" "${SCAN_DIR}"
```

脚本会自动：
1. 解析所有 CSV 文件 (Node.js, Python, C#)
2. 分类许可证风险等级
3. 生成完整的 markdown 报告

## 排除项

项目自身的 package 没有说明 license 的情况不计入第三方依赖统计。

## 常见问题

| 问题 | 处理 |
|------|------|
| 双许可证 (如 MIT OR GPL) | 选择更宽松的许可证 |
| UNKNOWN 许可证 | 检查包的 GitHub/npm/PyPI 页面确认 |
| MPL-2.0 包 | 未修改可使用，记录在报告中 |
| 项目自身包显示 UNLICENSED | 非第三方依赖，不计入风险统计 |

### Step 5: AI 审查并优化报告

脚本生成报告后，需要 AI 审查"需要关注的依赖"部分，提供更详细的分析和处理建议：

1. 读取生成的 `${SCAN_DIR}/04-license/license.md`
2. 对于每个中/高风险依赖，分析：
   - 该包的实际用途和必要性
   - 是否为双许可证（如 MIT OR GPL），选择更宽松的许可证
   - 是否未修改使用（MPL-2.0 未修改可接受）
   - 是否需要法务审查
3. 更新"需要关注的依赖"表格，添加详细说明列

**示例格式：**

```markdown
### 中风险许可证 (MPL-2.0)

| 包名 | 版本 | 许可证 | 说明 |
|------|------|--------|------|
| certifi | 2026.1.4 | MPL-2.0 | Python SSL 证书包，未修改使用，✅ 可接受 |
| tqdm | 4.66.5 | MIT + MPL-2.0 | 双许可证，选择 MIT，✅ 可接受 |
```

4. 更新结论部分，确认所有中风险依赖已评估通过
5. 保存更新后的报告到 `${SCAN_DIR}/04-license/license.md` 和 `${SCAN_DIR}/result/license.md`

## 完成标志

- [ ] `${SCAN_DIR}/04-license/license.md` 存在
- [ ] `${SCAN_DIR}/result/license.md` 存在
- [ ] 无高风险许可证 (或已记录豁免)
- [ ] 中风险依赖已 AI 审查并添加处理建议
- [ ] **Node.js 目录验证**: `nodejs-dirs.txt` 中所有目录已逐个检查，有 `node_modules` 的目录均已生成对应 CSV 文件
- [ ] **Python 目录验证**: `python-dirs.txt` 中所有 `requirements.txt` 文件已逐个安装依赖
- [ ] **报告完整性验证**: `license.md` 中的"完整依赖列表"包含通过 Python 脚本生成的全部所有依赖（Node.js 和 Python）

**记录用时**:
```bash
echo "STEP_04_END=$(date +%s)" >> security-scan-results/.current-scan
```

## 下一步

完成后继续执行 [05-trivy-scan.md](05-trivy-scan.md)
