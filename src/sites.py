# -*- coding: utf-8 -*-
"""网站数据池：把要收集的网站按「学习 / 工作 / 娱乐 / 生活」分类放在这里。

选网站的两条硬性规则：
  1. 在国内不用翻墙就能直接打开；
  2. 避开名气特别大的头部网站（B站、知乎、豆瓣、腾讯阿里系大产品等国民级网站不放进来）。

每一项的 key（如 shanbay）是网站的「唯一编号」，用于记录这个网站是否已被选用过，
避免不同日期重复收集同一个网站。key 一经定下不要再改动，否则去重会失效。

如果你觉得哪几个网站名气还是偏大、或想补充你觉得更好的网站，直接在这里增删即可。
"""

SITE_POOL = {
    "学习": {
        "shireny": {"name": "菜鸟教程", "url": "https://www.runoob.com"},
        "imooc": {"name": "慕课网", "url": "https://www.imooc.com"},
        "yixi": {"name": "一席", "url": "https://yixi.tv"},
        "xuetangx": {"name": "学堂在线", "url": "https://www.xuetangx.com"},
        "51zxw": {"name": "我要自学网", "url": "https://www.51zxw.net"},
        "shanbay": {"name": "扇贝单词", "url": "https://www.shanbay.com"},
        "mdn": {"name": "MDN 开发者文档", "url": "https://developer.mozilla.org"},
        "nlc": {"name": "国家图书馆公开课", "url": "https://www.nlc.cn"},
    },
    "工作": {
        "mubu": {"name": "幕布", "url": "https://mubu.com"},
        "processon": {"name": "ProcessOn", "url": "https://www.processon.com"},
        "jianguoyun": {"name": "坚果云", "url": "https://www.jianguoyun.com"},
        "worktile": {"name": "Worktile", "url": "https://worktile.com"},
        "tower": {"name": "Tower", "url": "https://tower.im"},
        "jiandaoyun": {"name": "简道云", "url": "https://www.jiandaoyun.com"},
        "wondercv": {"name": "超级简历", "url": "https://www.wondercv.com"},
        "yuque": {"name": "语雀", "url": "https://www.yuque.com"},
    },
    "娱乐": {
        "gcores": {"name": "机核网", "url": "https://www.gcores.com"},
        "5sing": {"name": "5sing原创音乐", "url": "https://5sing.kugou.com"},
        "xiaoyuzhou": {"name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com"},
        "acfun": {"name": "AcFun", "url": "https://www.acfun.cn"},
        "lofter": {"name": "LOFTER", "url": "https://www.lofter.com"},
        "eentry": {"name": "耳聆网", "url": "https://www.eentry.cn"},
        "bh3": {"name": "崩坏3官网", "url": "https://www.bh3.com"},
        "yangshipin": {"name": "央视频", "url": "https://www.yangshipin.cn"},
    },
    "生活": {
        "manmanbuy": {"name": "慢慢买", "url": "https://www.manmanbuy.com"},
        "meishij": {"name": "美食杰", "url": "https://www.meishij.net"},
        "douguo": {"name": "豆果美食", "url": "https://www.douguo.com"},
        "chunyuyisheng": {"name": "春雨医生", "url": "https://www.chunyuyisheng.com"},
        "qyer": {"name": "穷游", "url": "https://www.qyer.com"},
        "boqii": {"name": "波奇宠物", "url": "https://www.boqii.com"},
        "modian": {"name": "摩点", "url": "https://www.modian.com"},
        "weather": {"name": "中国天气网", "url": "https://www.weather.com.cn"},
    },
}

# 每天每个分类选几个网站，加起来要等于 10
CATEGORY_DISTRIBUTION = {"学习": 3, "工作": 2, "娱乐": 3, "生活": 2}