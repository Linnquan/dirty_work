# dirty_work

这里备份一些可复用的 Codex skills。

## getdata自动化平替

位置：`codex-skills/getdata-auto-replacement`

用途：从论文图、截图、扫描图里提取曲线趋势点或散点点位，并在 Codex 页面直接输出可复制到 Excel 的制表符表格（TSV）。它不会把 Excel 文件作为默认结果给你。

适合的问题：

- “帮我提取这张图里的曲线数据”
- “像 GetData 一样把图上的点位数字化”
- “这张散点图只有点，帮我把每个点的横纵坐标整理出来”
- “输出成我能直接复制进 Excel 的表格”

### 安装方法

1. 下载或克隆这个仓库。
2. 把 `codex-skills/getdata-auto-replacement` 整个文件夹复制到你的 Codex skills 目录：

```powershell
Copy-Item -Recurse -Force .\codex-skills\getdata-auto-replacement "$env:USERPROFILE\.codex\skills\getdata-auto-replacement"
```

3. 重新打开 Codex，或开启一个新对话，让 skill 被重新发现。

### 使用方法

在 Codex 里上传图片，然后调用：

```text
$getdata-auto-replacement
```

输出会直接显示为这种表格，整段复制到 Excel 会自动分列：

```text
点位编号	Depth_cm	年份	备注
1	2.53	2007.7	估计
2	4.51	2003.9	估计
```

### 说明

- 这个 skill 默认提取“代表整体趋势”的点位，不追求逐像素高密度复原。
- 如果图里只有散点或独立点位，它会直接提取每个点。
- 如果坐标轴、点位或曲线重叠不清，结果会在 `备注` 列或回复文字中提示需要人工复核。
- 坐标轴默认按线性坐标处理；如果是对数轴或特殊坐标，需要在提问时说明。
