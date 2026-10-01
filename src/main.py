# -*- coding: utf-8 -*-
"""每日精选网站收集程序（AI 选站版）。

运行流程：
  1. 读取 data/used.json，得到【全部历史记录过的网址】（只记录网址）；
  2. 由 DeepSeek「负责抓取选站」：让模型挑出 10 个国内不用翻墙、非大众知名、
     尽量不与历史重复的网站，给出格式化的网址清单；
  3. 程序对模型给出的网址做格式校验、与全部历史网址去重；数量不足时，
     自动回退内置候选池（src/sites.py / fetcher 的联网源）补齐，保证每天都够 10 个；
  4. 对每个网址调用 DeepSeek，用最直白的话介绍特点与功能，并给出所属分类；
  5. 按四类把介绍生成一篇 Word 文档，存到 docs/ 目录；
  6. 更新 data/used.json，把本次实际采用的网址追加进历史记录（只记网址）。

需要环境变量：DEEPSEEK_API_KEY。
可选：URL_SOURCE、QQ_MAIL_ADDR + QQ_MAIL_AUTH_CODE。
"""
import json
import os
import random
import re
import smtplib
import sys
from datetime import datetime
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import html
import requests
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from fetcher import fetch_candidates_all

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-flash"
EXPECTED_TOTAL = 10

CATEGORIES = ["学习", "工作", "娱乐", "生活"]

# 精简黑名单：漏网概率最高的几个大众平台域名。AI 挑中这些会被程序直接拦下。
BLOCKED_DOMAINS = [
    "bilibili.com", "b23.tv",
    "zhihu.com", "douban.com",
    "weibo.com", "weibo.cn",
    "douyin.com", "kuaishou.com",
    "baidu.com",
    "tencent.com", "qq.com",
    "163.com", "netease.com",
    "youku.com", "iqiyi.com", "aiqiyi.com",
    "sohu.com", "sina.com.cn",
    "jd.com", "taobao.com", "tmall.com", "pinduoduo.com",
    "meituan.com", "ctrip.com",
    "openai.com", "google.com", "grok.com", "x.com",
    "anthropic.com", "claude.ai", "meta.ai",
]

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "used.json"
DOCS_DIR = REPO_ROOT / "docs"

SEPARATORS = ("|", "｜", "|", "：")


def get_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        sys.exit("错误：没有找到 DEEPSEEK_API_KEY 环境变量，请在脚本或设置里配置 DeepSeek API 密钥。")
    return key


def _call_deepseek(prompt, temperature=0.7):
    """调用 DeepSeek 一次，返回文本。"""
    headers = {"Authorization": f"Bearer {get_api_key()}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def load_used():
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return {"urls": data.get("urls", []), "updated": data.get("updated", "")}
    return {"urls": [], "updated": ""}


def save_used(used):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(used, ensure_ascii=False, indent=2), encoding="utf-8")


def _valid_url(url):
    u = urlparse(url)
    return u.scheme in ("http", "https") and bool(u.netloc)


def _is_blocked(url):
    host = urlparse(url).netloc.lower()
    return any(domain in host for domain in BLOCKED_DOMAINS)


def _query_target(url):
    """从跳转链接的参数里提取真实目标地址（如 blogtalk.org/go?link=https%3A//x.com）。"""
    qs = urlparse(url).query
    if not qs:
        return None
    for key in ("link", "l", "url", "u", "target", "redirect", "next"):
        vals = parse_qs(qs).get(key)
        if vals and vals[0].startswith(("http://", "https://")):
            return vals[0]
    return None


def ask_ai_candidates(api_key, target, used_urls, rounds=6):
    """由 AI 负责抓取选站：让模型挑 target 个不重复的候选网址，返回 {url: {name, category}}。

    会对模型给出的网址做格式校验、与历史及本批去重、并按黑名单过滤大众平台；
    一轮不够就问下一轮，最多 rounds 轮。说明：模型凭其知识“回忆”网址，无法保证
    每个网址一定可达或国内可直连，程序已做格式与黑名单校验。
    """
    used = set(used_urls)
    result, seen = [], set()
    avoid = "、".join(list(used)[-30:]) or "（无）"

    for _ in range(rounds):
        need = target - len(result)
        if need <= 0:
            break
        prompt = (
            f"请你扮演“挑选网站的人”，帮我列出 {need} 个网站。要求：\n"
            f"1. 这些网站在中国大陆不用翻墙就能直接打开，且都是真实存在、能正常打开的网站，不要编造不存在的网址，拿不准就换一个；\n"
            f"2. 尽量覆盖 学习、工作、娱乐、生活 这四类；\n"
            f"3. 千万别选那些‘人人皆知的大平台’，例如：哔哩哔哩、知乎、豆瓣、微博、抖音、快手、微信、百度、腾讯QQ、网易、优酷、爱奇艺、腾讯视频、搜狐、新浪、京东、淘宝、天猫、拼多多、美团、携程等，以及这些平台旗下的任何主力产品都算；\n"
            f"4. 多挑一些“垂直、细分、冷门但真实有用”的网站，比如某个领域的小众学习站、小众工具站、小众兴趣社区等，越不为人所知越欢迎；\n"
            f"5. 不要和下面这些已经用过的网址重复：{avoid}\n"
            f"6. 严格按这个格式输出，每行一个网站，共 {need} 行：\n"
            f"网站名称 | https://完整网址 | 分类\n"
            f"（分类只能填：学习、工作、娱乐、生活 之一）\n"
            f"只输出这个列表，不要任何讲解。"
        )
        try:
            text = _call_deepseek(prompt, temperature=1.0)
        except Exception as e:
            print(f"  AI 挑选网站第 {_ + 1} 轮出错：{e}")
            continue

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            for sep in SEPARATORS:
                if sep in line:
                    parts = [p.strip() for p in line.split(sep)]
                    break
            else:
                continue
            if len(parts) < 2:
                continue
            name = parts[0].lstrip("0123456789.、 ")
            # 尝试从第 2 个字段提取完整网址
            url = parts[1]
            if not url.startswith(("http://", "https://")):
                continue
            url = url.rstrip(".,，。；;").rstrip("/")
            category = parts[2].removesuffix("）") if len(parts) > 2 else "生活"
            category = category.strip()
            if category not in CATEGORIES:
                category = "生活"
            if not _valid_url(url) or _is_blocked(url) or url in used or url in seen:
                continue
            seen.add(url)
            result.append({"name": name, "url": url, "category": category})

    return {item["url"]: {"name": item["name"], "category": item["category"]} for item in result}


def select_urls(candidates, used_urls, target=EXPECTED_TOTAL):
    """从候选里随机抽取 target 个与全部历史不重复的网址；不足时提示并保护补齐。"""
    candidates = dict(candidates)
    for url in list(candidates):
        if not _valid_url(url) or _is_blocked(url):
            candidates.pop(url, None)
    pool = list(candidates)
    random.shuffle(pool)

    chosen = []
    for url in pool:
        if url in used_urls:
            if url in candidates:
                candidates.pop(url, None)
            continue
        chosen.append(url)
        if len(chosen) >= target:
            break

    if len(chosen) < target:
        print(f"警告：可用新网址不足，目标 {target}，已选出 {len(chosen)} 个，将允许少量重复补齐。")
        for url in list(candidates):
            if url not in chosen:
                chosen.append(url)
            if len(chosen) >= target:
                break
    return chosen


def fetch_week_new_sites():
    """周日观测：联网抓取 WEEKLY_SOURCES(逗号分隔的可访问网页) 里的外链，过滤并去重后返回候选。"""
    raw = os.environ.get("WEEKLY_SOURCES", "").strip()
    if not raw:
        return None, "本周观测源未配置（可为每周工作流设置 WEEKLY_SOURCES，值为用逗号分隔的可访问网页地址）"
    used = set(load_used()["urls"])
    seen = set()
    candidates = []
    for src in raw.split(","):
        src = src.strip()
        if not src:
            continue
        try:
            src_host = urlparse(src).netloc.lower()
            # 观测源可能有过期/自签证书，仅用于抓取公开列表页，故关闭证书校验并抑制告警
            try:
                requests.packages.urllib3.disable_warnings(
                    requests.packages.urllib3.exceptions.InsecureRequestWarning
                )
            except Exception:
                pass
            r = requests.get(
                src,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=25,
                verify=False,
            )
            if r.status_code != 200:
                continue
            for mm in re.finditer(r'<a[^>]+href=["\'](https?://[^"\'\s#]+)["\'][^>]*>(.*?)</a>', r.text, re.I | re.S):
                href = mm.group(1).strip().rstrip('.,，。；;')
                label = re.sub(r"<[^>]+>", "", mm.group(2)).strip()
                real = _query_target(href)
                if real:
                    href = real
                if not _valid_url(href) or _is_blocked(href):
                    continue
                host = urlparse(href).netloc.lower()
                if host.count(".") < 1:
                    continue
                if host == src_host or host.endswith("." + src_host):
                    continue
                if href in used or href in seen:
                    continue
                seen.add(href)
                name = (html.unescape(label) if label else host)[:30].strip()
                candidates.append({"host": host, "name": name, "url": href})
        except Exception as e:
            print(f"  周日观测来源抓取失败：{src} {e}")
    byhost = {}
    for c in candidates:
        byhost.setdefault(c["host"], c)
    items = list(byhost.values())[:20]
    return items, f"本篇依据采集到的链接整理（来源：{raw}）；受来源所限可能含上线较早的站点，请以实际为准。"


def collect_weekly():
    items, note = fetch_week_new_sites()
    if not items:
        return {"items": [], "note": note}
    out = []
    for it in items[:10]:
        try:
            t = _call_deepseek(
                f"用一句最直白、不含专业术语的话，告诉普通人这个网站是干什么的：站名「{it['name']}」 网址 {it['url']}。只回那一句话。"
            )
            t = t.strip().splitlines()[0].strip()
        except Exception as e:
            t = ""
        out.append({"name": it["name"], "url": it["url"], "note": t})
    return {"items": out, "note": note}


def ask_model(name, url):
    """介绍单个网站，返回文本（含分类）。"""
    prompt = (
        f"请你用最准确、最直白的日常中文（绝对不要使用任何专业术语、技术词汇、英文缩写），"
        f"给普通人介绍下面这个网站。\n"
        f"网站名称：{name}\n网站网址：{url}\n\n"
        f"请严格按照下面的格式输出，每一项各占一行：\n"
        f"【分类】只能填一个，从这四个里选一个：学习、工作、娱乐、生活\n"
        f"【简介】用一两句话说明这个网站是什么、用来干什么\n"
        f"【特点】写出 2 到 3 点它的突出优点\n"
        f"【功能】写出 2 到 3 点它能帮人做什么事\n"
        f"【适合人群】用一句话说明适合什么人使用\n"
        f"不要输出其他任何内容。"
    )
    return _call_deepseek(prompt)


def parse_sections(text):
    sections = {"分类": "生活", "简介": "", "特点": "", "功能": "", "适合人群": ""}
    for key in sections:
        m = re.search(rf"【{key}】(.*?)(?=【|$)", text, re.S)
        if m:
            value = m.group(1).strip()
            if key == "分类":
                value = value.split(",")[0].strip() if value else "生活"
                value = value if value in CATEGORIES else "生活"
            sections[key] = value
    return sections


def build_docx(title, grouped, weekly=None):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Microsoft YaHei"
    style.font.size = Pt(11)
    from docx.oxml.ns import qn

    style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

    head = doc.add_heading(title, level=0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER

    intro = doc.add_paragraph(
        "本推荐每天自动生成，由 AI 挑选国内可访问的网站，按学习、工作、娱乐、生活四类归纳，"
        "用最直白的话告诉你每个网站的特点与功能。"
    )
    intro.alignment = WD_ALIGN_PARAGRAPH.CENTER
    intro.runs[0].font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    def _add_site(name, url, text):
        h = doc.add_heading(name, level=2)
        link = doc.add_paragraph()
        r = link.add_run(url)
        r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x9C)
        r.underline = True
        if not text:
            doc.add_paragraph("（这次没有拿到介绍内容）")
            return
        sections = parse_sections(text)

        def _add(title_txt, content):
            p = doc.add_paragraph(style="List Bullet")
            r = p.add_run(title_txt + "：")
            r.bold = True
            p.add_run(content)

        if sections["简介"]:
            _add("简介", sections["简介"])
        if sections["特点"]:
            _add("特点", sections["特点"].replace("\n", "；"))
        if sections["功能"]:
            _add("功能", sections["功能"].replace("\n", "；"))
        if sections["适合人群"]:
            _add("适合人群", sections["适合人群"])
        doc.add_paragraph()

    for category in CATEGORIES:
        items = grouped.get(category)
        if not items:
            continue
        doc.add_heading(category, level=1)
        for it in items:
            _add_site(it["name"], it["url"], it["text"])

    if weekly is not None:
        doc.add_page_break()
        doc.add_heading("本周新上线网站观察（周日版）", level=1)
        note = doc.add_paragraph(weekly.get("note", ""))
        if note.runs:
            note.runs[0].font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        if weekly.get("items"):
            for it in weekly["items"]:
                doc.add_heading(it["name"], level=2)
                lp = doc.add_paragraph()
                r = lp.add_run(it["url"])
                r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x9C)
                r.underline = True
                if it.get("note"):
                    doc.add_paragraph(it["note"])
        else:
            doc.add_paragraph("本周未能获取到可靠的新网站数据。")
    return doc


def send_email(attach_path, title_text):
    addr = os.environ.get("QQ_MAIL_ADDR", "").strip()
    code = os.environ.get("QQ_MAIL_AUTH_CODE", "").strip()
    if not addr or not code:
        print("跳过邮件发送：未配置 QQ_MAIL_ADDR 或 QQ_MAIL_AUTH_CODE")
        return

    msg = MIMEMultipart()
    msg["From"] = addr
    msg["To"] = addr
    msg["Subject"] = Header(title_text, "utf-8")
    msg.attach(MIMEText("你好，今天的网站推荐文档已生成，请查收附件。\n", "plain", "utf-8"))

    with open(attach_path, "rb") as f:
        part = MIMEApplication(f.read())
    filename = Path(attach_path).name
    part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", filename))
    msg.attach(part)

    server = smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=60)
    server.login(addr, code)
    server.sendmail(addr, [addr], msg.as_string())
    server.quit()
    print(f"已发送邮件到 {addr}，附件：{filename}")


def main():
    api_key = get_api_key()
    used = load_used()
    used_urls = set(used["urls"])

    print(f"历史已记录 {len(used_urls)} 个网址，让 AI 挑选 {EXPECTED_TOTAL} 个网站……")
    candidates = ask_ai_candidates(api_key, EXPECTED_TOTAL, used_urls)
    print(f"AI 挑出并通过校验的去重网址：{len(candidates)} 个")

    # 数量不足时回退内置候选池补齐
    if len(candidates) < EXPECTED_TOTAL:
        builtin = fetch_candidates_all()
        for url, info in builtin.items():
            if url not in candidates and _valid_url(url):
                candidates.setdefault(url, info)
        print(f"已用内置候选池补齐，现共有备选网址：{len(candidates)} 个")

    chosen_urls = select_urls(candidates, used_urls, EXPECTED_TOTAL)
    print(f"本次去重后实际采用 {len(chosen_urls)} 个网址。")

    items = []
    for url in chosen_urls:
        info = candidates.get(url, {})
        name = info.get("name") or url
        try:
            text = ask_model(name, url)
        except Exception as e:
            print(f"  [{name}] 出错：{e}，稍后重试一次……")
            try:
                text = ask_model(name, url)
            except Exception as e2:
                print(f"  [{name}] 重试仍失败，跳过此网站：{e2}")
                text = ""
        item = {"name": name, "url": url, "text": text}
        item["category"] = parse_sections(text)["分类"] if text else info.get("category", "生活")
        items.append(item)

    grouped = {c: [] for c in CATEGORIES}
    for it in items:
        grouped.setdefault(it["category"], []).append(it)

    today = datetime.now()
    date_label = today.strftime("%Y%m%d")
    title = f"每日精选网站推荐 · {today.strftime('%Y年%m月%d日')}"

    weekly = None
    if today.weekday() == 6 or os.environ.get("FORCE_WEEKLY"):
        weekly = collect_weekly()
        print(f"周日观测：{weekly['note']}")

    doc = build_docx(title, grouped, weekly=weekly)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOCS_DIR / f"每日网站推荐_{date_label}.docx"
    doc.save(str(out_path))
    print(f"已生成：{out_path}")

    try:
        send_email(out_path, title)
    except Exception as e:
        print(f"邮件发送失败（不影响文档已生成）：{e}")

    used["urls"] = list(dict.fromkeys(list(used["urls"]) + chosen_urls))
    used["updated"] = today.strftime("%Y-%m-%d %H:%M:%S")
    save_used(used)
    print(f"已追加 {len(chosen_urls)} 个网址到历史记录，避免下次重复。")


if __name__ == "__main__":
    main()