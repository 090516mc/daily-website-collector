# 每日精选网站收集

一个部署在 GitHub Actions 上的自动化程序：**每天自动挑选 10 个网站，生成介绍，并整理成一篇 Word 文档。**

- **每天随机抓取 10 个网址**（联网候选源 / 内置候选池），由程序负责抓取与挑选。
- **去重**：`data/used.json` 只记录网址，每天与**全部历史网址**对比，重复的丢弃并补抓，保证当天 10 个网址与历史不重复。
- **模型负责介绍**，调用 DeepSeek 的 **deepseek-v4-flash**（按量付费，每天成本约 1 分钱），用**最直白、不含专业术语**的大白话说明每个网址的特点与功能，并判定其属于**学习 / 工作 / 娱乐 / 生活**哪一类，文档按这四类分组展示。
- 生成的 Word 文档保存到 `docs/` 目录，自动提交回 GitHub 仓库，**并通过 QQ 邮箱把文档作为附件发到你的邮箱**。

## 目录结构

```
daily-website-collector/
├── .github/workflows/daily.yml   # 每天自动运行的定时任务
├── src/
│   ├── main.py                   # 主程序：抓取去重 + 调模型 + 生成 Word
│   ├── fetcher.py                # 网址来源：联网候选源 / 内置池，可扩展
│   └── sites.py                  # 内置兜底候选池（可自行增删）
├── data/used.json                # 仅记录历史用过的网址（用于去重）
├── requirements.txt              # 依赖
└── README.md
```

## 部署步骤

### 1. 获取 DeepSeek API 密钥

1. 打开 DeepSeek 开放平台 [platform.deepseek.com](https://platform.deepseek.com) 注册登录；
2. 进入「API Keys」页面，点击创建 API Key（形如 `sk-xxxx`），复制保存好。

> 建议先给 DeepSeek 账户充少量金额（几元就够用很久）：deepseek-v4-flash 下每天生成一份文档成本约 1 分钱，一年也就几块钱，按实际用量扣费，无固定月费。

### 2. 把项目推到 GitHub

在 GitHub 上新建一个**私有仓库**（Private 即可），然后把本目录内容推上去：

```bash
cd daily-website-collector
git init
git add .
git commit -m "init"
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 3. 配置密钥（关键）

在仓库 **Settings → Secrets and variables → Actions → New repository secret** 中依次添加 3 个密钥：

| Secret 名 | 填什么 |
|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek 的 API Key（`sk-xxxx`） |
| `QQ_MAIL_ADDR` | 发件 QQ 邮箱地址，如 `mrl090516@qq.com` |
| `QQ_MAIL_AUTH_CODE` | 该 QQ 邮箱的 SMTP 授权码（在 QQ 邮箱「设置 → 账户 → 开启 POP3/SMTP 服务」后生成的码） |

> 授权码不是 QQ 密码，需单独开启 SMTP 服务并生成。每天生成的文档会以附件形式发送到发件邮箱（目前收件=发件）。

### 4. 手动跑一次试试

1. 打开仓库 → **Actions** 页面；
2. 左侧选「每日网站收集」，点击右上角 **Run workflow** → 绿色按钮触发一次；
3. 等运行完成后，回到仓库文件列表，打开 `docs/` 文件夹即可看到生成的 Word 文档；
4. 也可以查看每次运行的日志，检查是否成功。

> Actions 免费版每天运行时长充足，每天自动运行一次完全够用，无需付费。

## 每天运行时间

工作流默认 **每天 02:00（世界协调时间）**运行，即**北京时间上午 10:00**。

想改时间，编辑 `.github/workflows/daily.yml` 里的这一行（cron 是 UTC 时间）：

```yaml
- cron: "0 2 * * *"   # 分 时 日 月 周
```

例如想改成北京时间早上 8 点跑，就是 UTC 时间 0 点，改成 `0 0 * * *`。

## 网址来源与去重逻辑

- **网址来源**：默认从 `src/sites.py` 的内置候选池（已筛「国内可直连、非大众知名」）随机抓取；
  如需「真正联网从任何地方抓取」，可设置环境变量 / 仓库 Secret：`URL_SOURCE` 为一个**在线 JSON 网址列表**的地址，
  格式 `[ {"name":"站名","url":"https://..."}, ... ]` 或 `["https://...", ...]`，
  程序每天会联网拉取这份候选；拉取失败时自动回退内置池，保证每天都能跑出来。
- **去重规则**：`data/used.json` **只记录网址**（不记网站其他信息）。每天随机抓取后，与【全部历史网址】对比，
  重复的网址被丢弃并补抓新的，直到凑满 10 个与历史不重复的网址。
- **分类**：抓到的网址由模型判断属于 学习 / 工作 / 娱乐 / 生活 哪一类，文档按这四类分组展示。

## 扩展点（方便以后改程序）

- 换网址来源：改 `src/fetcher.py` 里的 `fetch_candidates_all()`，或配置 `URL_SOURCE`；
- 加可访问性 / 是否翻墙筛查：改 `src/fetcher.py` 里的 `screen()`；
- 改每天数量：改 `main.py` 里的 `EXPECTED_TOTAL`；
- 增删内置兜底网站：编辑 `src/sites.py` 的 `SITE_POOL`。

## 常见问题

- **生成的文档是空的 / 没有介绍内容**：多半是 API 密钥没配置或余额不足，检查仓库里的 `DEEPSEEK_API_KEY` 密钥及账户余额，并查看 Actions 运行日志。
- **某天网址不足 10 个 / 提示「可用的新网址不足」**：说明内置候选源里可用的新网址已被历史记录占用得差不多了，需扩充 `src/sites.py` 候选池，或配置 `URL_SOURCE` 提供更大的网址来源。