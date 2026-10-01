# -*- coding: utf-8 -*-
"""网址来源模块。

职责：提供『候选网址』给主程序从中随机挑选。
初版实现了两层来源，可随时替换/扩展：
  1. 在线候选源：通过环境变量 URL_SOURCE 指定一个「在线 JSON 网址列表」地址，
     程序每天联网拉取一批候选网址（真正做到“从任何地方抓取”）。
  2. 内置兜底池：当在线源未配置或拉取失败时，回退到 src/sites.py 里维护的、
     已筛过「国内可直连 + 非大众知名」的候选池，保证程序每天至少能跑出来。

扩展点：
  - 想换/增一个网址来源：改 fetch_candidates_all()；
  - 想对候选网址做可访问性、是否需翻墙等筛查：改 screen()。
"""
import os

import requests

from sites import SITE_POOL

ONLINE_SOURCE = os.environ.get("URL_SOURCE", "").strip()


def _builtin_candidates():
    """从内置池整理出 {url: {name}}。"""
    out = {}
    for _category, items in SITE_POOL.items():
        for _key, info in items.items():
            out.setdefault(info["url"].rstrip("/"), {"name": info["name"]})
    return out


def _fetch_online(source):
    """联网拉取候选网址。

    支持两种格式：
      [ {"name": "站名", "url": "https://..."}, ... ]   或
      [ "https://...", ... ]
    """
    try:
        resp = requests.get(source, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"警告：在线网址源拉取失败，改用内置候选池兜底。原因：{e}")
        return {}

    if not isinstance(data, list):
        print("警告：在线网址源返回的不是列表，改用内置候选池兜底。")
        return {}

    out = {}
    for item in data:
        if isinstance(item, dict) and item.get("url"):
            url = str(item["url"]).rstrip("/")
            out[url] = {"name": str(item.get("name") or url)}
        elif isinstance(item, str) and item.startswith("http"):
            out[item.rstrip("/")] = {"name": item.rstrip("/")}
    if not out:
        print("警告：在线网址源没有解析出任何有效网址，改用内置候选池兜底。")
    return out


def screen(candidates):
    """（扩展点）对候选网址做进一步筛查，例如探测是否可访问、是否需翻墙。

    初版直接返回，不做网络探测——因为云端运行环境在海外，无法可靠判断某网址
    在国内能否直连。如需更准的可访问性筛查，可在此补充对每个 url 的探测逻辑。
    """
    return candidates


def fetch_candidates_all():
    """返回全部候选网址映射 url -> {name}。"""
    merged = {}
    if ONLINE_SOURCE:
        merged.update(screen(_fetch_online(ONLINE_SOURCE)))
    if not merged:
        builtin = screen(_builtin_candidates())
        print(f"使用内置候选池，共 {len(builtin)} 个备选网址。")
        merged = builtin
    else:
        print(f"使用在线网址源，共 {len(merged)} 个备选网址。")
    return merged