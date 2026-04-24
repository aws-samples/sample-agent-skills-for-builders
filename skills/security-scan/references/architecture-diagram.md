# 架构图获取

## 目标

获取项目的架构图，用于安全审查和文档提交。

## 执行步骤

### Step 1: 获取扫描目录

```bash
source security-scan-results/.current-scan
echo "输出目录: ${SCAN_DIR}/01-architecture/"
```

### Step 2: 查找架构图

架构图通常在 README.md 文档前面部分展示，常见位置：
- `docs/images/architecture.png`
- `docs/images/architecture.jpg`
- `docs/architecture.png`
- `architecture.png`
- `images/architecture.png`

检查 README 中的架构图引用：
```bash
grep -E "!\[.*\]\(.*\.(png|jpg|svg)" README.md | head -5
```

自动查找架构图文件：
```bash
# 查找可能的架构图文件
ARCH_FILE=$(find "$PROJECT_ROOT" -type f \( -name "architecture*.png" -o -name "architecture*.jpg" -o -name "architecture*.svg" \) \
    -not -path "*/node_modules/*" -not -path "*/cdk.out/*" -not -path "*/.git/*" | head -1)

if [ -z "$ARCH_FILE" ]; then
    # 如果没找到 architecture 命名的文件，查找 docs/images 下的图片
    ARCH_FILE=$(find "$PROJECT_ROOT/docs" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.svg" \) 2>/dev/null | head -1)
fi

echo "找到架构图: $ARCH_FILE"
```

### Step 3: 复制架构图到结果目录

找到架构图后，复制到扫描结果目录和 result 目录：

```bash
if [ -n "$ARCH_FILE" ]; then
    # 获取文件扩展名
    EXT="${ARCH_FILE##*.}"

    # 复制到 01-architecture 目录
    cp "$ARCH_FILE" "${SCAN_DIR}/01-architecture/diagram.${EXT}"

    # 同时复制到 result 目录（用于最终提交）
    cp "$ARCH_FILE" "${SCAN_DIR}/result/architecture.${EXT}"

    echo "架构图已复制"
else
    echo "未找到架构图文件，请手动指定路径"
fi
```

> **注意**: 如果自动查找未找到架构图，请根据项目实际情况手动指定路径。

### Step 4: 验证架构图

确认架构图已复制：
```bash
ls -la "${SCAN_DIR}/01-architecture/"
ls -la "${SCAN_DIR}/result/"
```

## 完成标志

- [ ] 架构图文件已复制到 `01-architecture/diagram.*`
- [ ] 架构图文件已复制到 `result/architecture.*`
- [ ] 如果项目没有架构图，记录说明并继续下一步

**记录用时**:
```bash
echo "STEP_01_END=$(date +%s)" >> security-scan-results/.current-scan
```

## 下一步

完成后继续执行 [02-cdk-synth.md](02-cdk-synth.md)
