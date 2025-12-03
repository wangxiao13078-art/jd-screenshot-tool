# 京东截图编辑工具

> ⚠️ 仅供内部培训、产品设计、个人存档使用

## 快速开始

### macOS / Linux

```bash
# 1. 安装（首次使用）
./install.sh

# 2. 启动
./start.sh

# 3. 打开浏览器访问
http://127.0.0.1:7860
```

### Windows

```
1. 双击 install.bat（首次使用）
2. 双击 start.bat 启动
3. 打开浏览器访问 http://127.0.0.1:7860
```

## 打包到其他机器

### 需要打包的文件

```
截图工具/
├── app.py               ✅ 必需
├── browser_screenshot.py ✅ 必需
├── image_editor.py       ✅ 必需
├── requirements.txt      ✅ 必需
├── install.sh           ✅ 必需 (Mac/Linux)
├── install.bat          ✅ 必需 (Windows)
├── start.sh             ✅ 必需 (Mac/Linux)
├── start.bat            ✅ 必需 (Windows)
├── README.md            📝 可选
└── venv/                ❌ 不要打包（每台机器重新生成）
```

### 打包命令

```bash
# 在截图工具目录的上级目录执行
cd ~/Downloads
zip -r 截图工具.zip 截图工具 -x "截图工具/venv/*" -x "截图工具/__pycache__/*" -x "截图工具/*.png"
```

### 在新机器上使用

**前提条件：**
- 安装 Python 3.8+ （[下载地址](https://www.python.org/downloads/)）
- 需要联网（安装依赖和浏览器）

**步骤：**
1. 解压 `截图工具.zip`
2. 运行安装脚本 `install.sh` 或 `install.bat`
3. 运行启动脚本 `start.sh` 或 `start.bat`
4. 浏览器访问 `http://127.0.0.1:7860`

## 使用方法

1. **获取图片**：输入京东URL截图，或上传本地截图
2. **编辑区域**：填写 X坐标、Y坐标、宽度、高度
3. **输入文字**：填写要替换的内容（如 ¥888.00）
4. **应用保存**：点击应用修改 → 保存图片

## 常见问题

**Q: 安装失败？**
- 确保已安装 Python 3.8+
- 确保网络通畅（需要下载依赖）

**Q: 截图显示登录页？**
- 京东部分页面需要登录
- 建议直接上传本地截图

**Q: 中文乱码？**
- 程序会自动查找系统字体
- 确保系统已安装中文字体

## 文件说明

| 文件 | 说明 |
|------|------|
| `app.py` | 主程序（Web界面） |
| `browser_screenshot.py` | 浏览器截图模块 |
| `image_editor.py` | 图片编辑模块 |
| `requirements.txt` | Python 依赖 |
| `install.sh/bat` | 安装脚本 |
| `start.sh/bat` | 启动脚本 |
