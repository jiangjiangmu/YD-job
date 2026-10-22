# ==========================================
# @job-desktop / 助手会话：zhipin-helper 接入与使用指南
# ==========================================

# 【一、项目物理资产定位】
# 1. 项目根目录：E:\AI\DeepSeek Harness\Vault\desktop\projects\zhipin-helper\
# 2. 数据与报告区：E:\AI\DeepSeek Harness\Vault\desktop\projects\zhipin-helper\data\
# 3. 配置文件：E:\AI\DeepSeek Harness\Vault\desktop\projects\zhipin-helper\config.yaml
# 4. 核心脚本：
#    - spider.py (浏览器 CDP 调试连接与岗位采集)
#    - analyzer.py (岗位匹配分析与打分)

# 【二、底层运行环境准备】
# 1. 浏览器复用机制：
#    本项目不采用无头浏览器，而是复用用户本地已登录 BOSS 直聘的 Chrome 实例。
#    Chrome 启动参数：--remote-debugging-port=9222 --user-data-dir="C:\Users\jiang\.dsh\chrome-debug-profile"
# 2. 连通性快速验证（PowerShell）：
#    & "$env:SystemRoot\System32\curl.exe" -s http://127.0.0.1:9222/json/version

# 【三、Python 运行环境】
# 1. 项目独立虚拟环境：E:\AI\DeepSeek Harness\Vault\desktop\projects\zhipin-helper\.venv\
#    （基座为干净官方 Python 3.12.10：C:\Users\jiang\AppData\Local\Programs\Python\Python312\python.exe，
#     已装 pandas / openpyxl / websocket-client / pyyaml）
# 2. ⚠️ 重要：不要用 DSH runtime python（C:\Users\jiang\.dsh\dsh-runtimes\...）运行本项目脚本——
#    该解释器内嵌文件写入沙箱（只允许写 DSH 会话工作区），写本项目目录会报 WinError 5 拒绝访问。

# 【四、快速上手与接管步骤（给新会话的指令）】
# Step 1: 检查 9222 端口是否存活，确认用户已在 Chrome 中打开 BOSS 直聘页面。
# Step 2: 运行采集脚本（务必用项目 venv 的解释器）：
#         cd E:\AI\DeepSeek Harness\Vault\desktop\projects\zhipin-helper
#         .venv\Scripts\python.exe spider.py
# Step 3: 查看生成的原始数据：data/raw_jobs.json（分页原始数据在 data/raw_pages/）
# Step 4: 运行分析脚本生成 Excel 报告：
#         .venv\Scripts\python.exe analyzer.py
#         输出：data/岗位分析报告_时间戳.xlsx（含岗位总表/兼职实习/统计与配置三个表）
# 备注：probe_wapi.py 为接口结构探测脚本，排障时可单独运行。
# ⚠️ 风控提醒：spider 采集节奏已调优（每词先导航搜索页 + wapi 间隔 10-18s）。
#    不要把 config.yaml 的 min/max_delay_seconds 调小，否则会触发 code=37「环境异常」，
#    一旦触发所有关键词全部失败，需人工在 Chrome 刷新直聘页面恢复。
# 采集关键词在 config.yaml 的 search.keywords（列表，多关键词合并去重）。
