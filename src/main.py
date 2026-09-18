# -*- coding: utf-8 -*-
"""每日精选网站收集程序。

运行流程：
  1. 读取 data/used.json，找出每个分类里还没被选过的网站；
  2. 程序按分类配额随机选 10 个网站（选过的不重复选）；
  3. 调用 DeepSeek（deepseek-v4-flash）模型，用最直白的话介绍每个网站的特点与功能；
  4. 把介绍生成一篇 Word 文档，保存到 docs/ 目录；
  5. 更新 data/used.json，把这次选中的网站标记为「已选」。

需要环境变量：DEEPSEEK_API_KEY（DeepSeek 的 API 密钥）
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

import requests
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from sites import SITE_POOL, CATEGORY_DISTRIBUTION

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-flash"
EXPECTED_TOTAL = 10

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "used.json"
DOCS_DIR = REPO_ROOT / "docs"


def get_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        sys.exit("错误：没有找到 DEEPSEEK_API_KEY 环境变量，请先在脚本或设置里配置 DeepSeek API 密钥。")
    return key


def load_used():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}


def save_used(used):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(used, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def select_sites(used):
    """从每个分类里挑选还没用过的网站，分类配额加起来正好 10 个。"""
    chosen = {}
    for category, need in CATEGORY_DISTRIBUTION.items():
        used_keys = set(used.get(category, []))
        all_items = list(SITE_POOL[category].items())
        available = [(k, v) for k, v in all_items if k not in used_keys]

        # 该分类可选的网站不够了，就把这个分类的选用记录清空重来
        if len(available) < need:
            available = all_items
            used[category] = []

        picked = random.sample(available, need)
        used_keys_now = set(used.get(category, []))
        for key, info in picked:
            used_keys_now.add(key)
            chosen[key] = info
        used[category] = list(used_keys_now)

    if len(chosen) != EXPECTED_TOTAL:
        sys.exit(f"错误：本次应选 {EXPECTED_TOTAL} 个网站，实际选了 {len(chosen)} 个。")
    return chosen


def ask_model(api_key, name, url):
    """调用 DeepSeek 模型，返回介绍文本。"""
    prompt = (
        f"请你用最准确、最直白的日常中文（绝对不要使用任何专业术语、技术词汇、英文缩写），"
        f"给普通人介绍下面这个网站。\n"
        f"网站名称：{name}\n网站网址：{url}\n\n"
        f"请严格按照下面的格式输出，每一项各占一行：\n"
        f"【简介】用一两句话说明这个网站是什么、用来干什么\n"
        f"【特点】写出 2 到 3 点它的突出优点\n"
        f"【功能】写出 2 到 3 点它能帮人做什么事\n"
        f"【适合人群】用一句话说明适合什么人使用\n"
        f"不要输出其他任何内容。"
    )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def parse_sections(text):
    """把模型返回的固定格式文本，拆成 {简介, 特点, 功能, 适合人群}。"""
    sections = {"简介": "", "特点": "", "功能": "", "适合人群": ""}
    for key in sections:
        m = re.search(rf"【{key}】(.*?)(?=【|$)", text, re.S)
        if m:
            sections[key] = m.group(1).strip()
    return sections


def build_docx(title, items):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Microsoft YaHei"
    style.font.size = Pt(11)
    from docx.oxml.ns import qn

    style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

    # 标题
    head = doc.add_heading(title, level=0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER

    intro = doc.add_paragraph(
        "本推荐每天自动生成，覆盖学习、工作、娱乐、生活四类，每个网站都经过模型挑选，"
        "用最直白的话告诉你它的特点与功能。"
    )
    intro.alignment = WD_ALIGN_PARAGRAPH.CENTER
    intro.runs[0].font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    for key, info in items:
        name, url = info["name"], info["url"]
        text = info.get("text", "")

        # 网站名 + 网址
        h = doc.add_heading(name, level=1)
        link = doc.add_paragraph()
        r = link.add_run(url)
        r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x9C)
        r.underline = True

        if not text:
            doc.add_paragraph("（这次没有拿到介绍内容）")
            continue

        sections = parse_sections(text)

        def _add(title_txt, content, bullet=False):
            p = doc.add_paragraph(style="List Bullet" if bullet else None)
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

        doc.add_paragraph()  # 间隔

    return doc


def send_email(attach_path, title_text):
    """通过 QQ 邮箱 SMTP 把生成的文档作为附件发到收件邮箱。

    需要环境变量 QQ_MAIL_ADDR（发件邮箱）与 QQ_MAIL_AUTH_CODE（SMTP 授权码）。
    未配置时跳过发送，不影响文档生成。
    """
    addr = os.environ.get("QQ_MAIL_ADDR", "").strip()
    code = os.environ.get("QQ_MAIL_AUTH_CODE", "").strip()
    if not addr or not code:
        print("跳过邮件发送：未配置 QQ_MAIL_ADDR 或 QQ_MAIL_AUTH_CODE")
        return

    msg = MIMEMultipart()
    msg["From"] = addr
    msg["To"] = addr  # 收件与发件相同；如需发到别的地址可在这里调整
    msg["Subject"] = Header(title_text, "utf-8")
    msg.attach(MIMEText("你好，今天的网站推荐文档已生成，请查收附件。\n", "plain", "utf-8"))

    with open(attach_path, "rb") as f:
        part = MIMEApplication(f.read())
    filename = Path(attach_path).name
    part.add_header("Content-Disposition", "attachment",
                    filename=("utf-8", "", filename))
    msg.attach(part)

    server = smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=60)
    server.login(addr, code)
    server.sendmail(addr, [addr], msg.as_string())
    server.quit()
    print(f"已发送邮件到 {addr}，附件：{filename}")


def main():
    api_key = get_api_key()
    used = load_used()
    chosen = select_sites(used)

    today = datetime.now()
    date_label = today.strftime("%Y%m%d")

    print(f"本次选出 {len(chosen)} 个网站，开始调用 DeepSeek 生成介绍……")
    items = []
    for key, info in chosen.items():
        try:
            text = ask_model(api_key, info["name"], info["url"])
        except Exception as e:
            print(f"  [{info['name']}] 出错：{e}，稍后重试一次……")
            try:
                text = ask_model(api_key, info["name"], info["url"])
            except Exception as e2:
                print(f"  [{info['name']}] 重试仍失败，跳过此网站：{e2}")
                text = ""
        info = dict(info)
        info["text"] = text
        items.append((key, info))

    title = f"每日精选网站推荐 · {today.strftime('%Y年%m月%d日')}"
    doc = build_docx(title, items)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOCS_DIR / f"每日网站推荐_{date_label}.docx"
    doc.save(str(out_path))
    print(f"已生成：{out_path}")

    try:
        send_email(out_path, f"每日精选网站推荐 · {today.strftime('%Y年%m月%d日')}")
    except Exception as e:
        print(f"邮件发送失败（不影响文档已生成）：{e}")

    save_used(used)
    print("已更新已选网站记录，避免明天重复。")


if __name__ == "__main__":
    main()