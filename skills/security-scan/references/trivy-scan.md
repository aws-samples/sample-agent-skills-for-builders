# Trivy 容器镜像扫描

## 目标

使用 Trivy 扫描 Docker 镜像中的安全漏洞，包括基础镜像的系统包和应用依赖。

## 前置条件

- 已安装 Docker
- 已安装 Trivy CLI（安装: https://github.com/aquasecurity/trivy）
- 已登录 ECR Public（避免 403 错误）

```bash
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

## 重要规则

1. **必须使用镜像扫描**：所有 Dockerfile 都必须构建镜像后使用 `trivy image` 扫描，禁止使用 `trivy fs` 文件系统扫描（不完整）
2. **顺序构建**：按顺序构建镜像，利用 Docker 层缓存（多个镜像共享基础镜像时更高效）
3. **修复循环**：发现漏洞后必须修复并重新构建、重新扫描，直到无 CRITICAL/HIGH 漏洞
4. **output.txt 规则**：仅在发现漏洞并修复后才生成 `output.txt`，无漏洞时只保留 `output_origin.txt`
5. **自动修复**：发现漏洞后必须立即自动修复，无需询问用户确认。只有在漏洞无法修复（如上游无修复版本）时才记录豁免说明
6. **最小改动原则**（同 `00-full-scan.md` 规则 5）：只修复安全问题，不改变业务逻辑
   - ✅ 直接修复：改动范围小（≤3 个文件，≤100 行代码）
   - ⏭️ 跳过并记录：需要修改业务实现逻辑或改动范围大
7. **构建失败重试**：镜像构建失败时最多重试 1 次，仍失败则跳过并记录

## 扫描方式说明

| 命令 | 扫描对象 | 内容 | 使用场景 |
|------|---------|------|---------|
| `trivy image` | Docker 镜像 | 基础镜像系统包 + 应用依赖 | **必须使用** |
| `trivy fs` | 本地文件系统 | 仅应用依赖文件 | ❌ 禁止使用 |

**本流程强制使用 `trivy image` 扫描构建后的镜像，确保扫描完整性。**

## 输出目录结构

```
05-trivy/
├── {image-name-1}/
│   ├── output_origin.txt    # 首次扫描原始输出（始终保留）
│   └── output.txt           # 修复后的扫描输出（仅当有漏洞需修复时创建）
├── {image-name-2}/
│   └── ...
└── fix-report.md            # 修复报告（如有修复）
```

## 执行步骤

### Step 1: 登录 ECR Public

```bash
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

### Step 2: 查找所有 Dockerfile

```bash
find "$PROJECT_ROOT" -name "Dockerfile*" -not -path "*/node_modules/*" -not -path "*/cdk.out/*" -not -path "*/.git/*"
```

### Step 3: 顺序构建并扫描所有镜像

**按顺序构建镜像**（利用 Docker 层缓存，多个镜像共享基础镜像时更高效）：

为每个 Dockerfile 执行：

```bash
# 创建输出目录
mkdir -p "${SCAN_DIR}/05-trivy/${image_name}"

# 构建镜像
docker build -t "trivy-scan-${image_name}:latest" -f "$dockerfile" "$dir"

# 扫描镜像（仅生成 output_origin.txt）
trivy image --severity HIGH,CRITICAL "trivy-scan-${image_name}:latest" > "${SCAN_DIR}/05-trivy/${image_name}/output_origin.txt" 2>&1
```

**为什么顺序构建更好**：
- 多个镜像共享相同基础镜像（如 `python:3.11-slim`）时，Docker 会缓存共享层
- 第一个镜像拉取基础镜像后，后续镜像直接使用缓存
- 避免并行构建时的资源竞争和磁盘 I/O 瓶颈

### Step 4: 分析扫描结果

检查每个镜像的 `output_origin.txt`：
- **CRITICAL**: 必须立即修复
- **HIGH**: 应该修复

### Step 5: 修复-重建-重扫循环

**发现漏洞后必须执行以下循环，直到无漏洞：**

```
发现漏洞 → 修复代码/依赖 → 重新构建镜像 → 重新扫描 → 检查结果
    ↑                                                    ↓
    └──────────── 仍有漏洞 ←─────────────────────────────┘
```

**修复后重新扫描**：

```bash
# 1. 修复 Dockerfile 或依赖文件

# 2. 重新构建镜像
docker build -t "trivy-scan-${image_name}:latest" -f "$dockerfile" "$dir"

# 3. 重新扫描，生成 output.txt
trivy image --severity HIGH,CRITICAL "trivy-scan-${image_name}:latest" > "${SCAN_DIR}/05-trivy/${image_name}/output.txt" 2>&1

# 4. 检查是否还有漏洞，如有则重复步骤 1-3
```

**常见修复方式**：

| 问题类型 | 修复方案 |
|---------|---------|
| 基础镜像漏洞 | 更新 FROM 到最新版本或使用 Alpine |
| 系统包漏洞 | 添加 `RUN apk upgrade` 或 `apt-get upgrade` |
| Python 依赖漏洞 | 更新 requirements.txt 中的版本 |
| Node.js 依赖漏洞 | 更新 package.json 中的版本 |

### Step 6: 清理镜像

扫描完成后删除所有临时镜像：

```bash
docker rmi "trivy-scan-portal:latest" "trivy-scan-tag-image:latest" ...
# 或批量删除
docker images | grep "trivy-scan-" | awk '{print $3}' | xargs docker rmi
```

### Step 7: 生成结果报告

生成 `${SCAN_DIR}/result/trivy.md`，仅包含：
1. 扫描摘要表格（镜像名、CRITICAL/HIGH 数量、状态）
2. 豁免漏洞说明（如有豁免）

**注意**: 修复记录和下一步建议放在 `fix-report.md` 中，不要放在 `result/trivy.md` 中。

## 完成标志

- [ ] 所有 Dockerfile 都已构建镜像并扫描
- [ ] 每个镜像目录下都有 `output_origin.txt`
- [ ] 无 CRITICAL 级别漏洞
- [ ] 无 HIGH 级别漏洞（或已记录豁免理由）
- [ ] `${SCAN_DIR}/result/trivy.md` 已生成
- [ ] 如有修复，`fix-report.md` 已创建，对应镜像有 `output.txt`
- [ ] 所有临时镜像已清理

**记录用时**:
```bash
echo "STEP_05_END=$(date +%s)" >> security-scan-results/.current-scan
```

## 下一步

完成后继续执行 [06-ash-scan.md](06-ash-scan.md)
