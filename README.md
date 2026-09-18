# 每日精选网站收集

一个部署在 GitHub Actions 上的自动化程序：**每天自动挑选 10 个网站，生成介绍，并整理成一篇 Word 文档。**

- 网站类型：**学习 / 工作 / 娱乐 / 生活** 四类，每天配额为 3 / 2 / 3 / 2，共 10 个。
- **程序负责选网站**，从 `src/sites.py` 的网站池里随机挑选，靠 `data/used.json` 记录，**保证不同日期不重复**。
- **模型负责介绍**，调用 DeepSeek 的 **deepseek-v4-flash**（按量付费，每天成本约 1 分钱），用**最直白、不含专业术语**的大白话说明每个网站的特点与功能。
- 生成的 Word 文档保存到 `docs/` 目录，自动提交回 GitHub 仓库，**并通过 QQ 邮箱把文档作为附件发到你的邮箱**。

## 目录结构

```
daily-website-collector/
├── .github/workflows/daily.yml   # 每天自动运行的定时任务
├── src/
│   ├── main.py                   # 主程序：选站 + 调模型 + 生成 Word
│   └── sites.py                  # 网站池（可自行增删）
├── data/used.json                # 已选过的网站记录（用于去重）
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

## 想调整网站或配额

已按你的要求筛选：**所有网站在国内不用翻墙即可打开**，且**都已排除名气特别大的头部网站**（如 B 站、知乎、豆瓣等国民级平台不放进来）。

- **增减网站**：编辑 `src/sites.py` 里的 `SITE_POOL`，在对应的分类下加一行即可；
- **改每天数量**：编辑 `src/sites.py` 末尾的 `CATEGORY_DISTRIBUTION`，让四类加起来等于 10。
- 改完后 `git push` 即可，工作流会自动使用新配置。

## 常见问题

- **生成的文档是空的 / 没有介绍内容**：多半是 API 密钥没配置或余额不足，检查仓库里的 `DEEPSEEK_API_KEY` 密钥及账户余额，并查看 Actions 运行日志。
- **某个网站总是不出现**：可能该网站此前已被选中过，去重记录还在，等记录清空或到该分类的网站都被用过一轮后会重新可选。