# -*- coding: utf-8 -*-
"""网站数据池：把要收集的网站按「学习 / 工作 / 娱乐 / 生活」分类放在这里。

选网站的三条硬性规则：
  1. 在国内不用翻墙就能直接打开；
  2. 避开名气特别大的头部网站（B站、知乎、豆瓣、抖音、腾讯/阿里/百度系大产品等国民级平台不放）；
  3. 尽量选真实存在、目前仍在正常运行的站点。

每一项的 key 是网站的「唯一编号」，用于记录这个网站是否已被选用过，避免不同日期重复。
key 一经定下不要再改动，否则去重会失效。

池子已扩充到每类约 30 个，配合每天 3/2/3/2 的配额，能让“网站不重复”维持更久。
如果你想增删网站，直接在对应分类里加/删一行即可。
"""

SITE_POOL = {
    "学习": {
        # 原有：可直连、知名度适中
        "runoob": {"name": "菜鸟教程", "url": "https://www.runoob.com"},
        "imooc": {"name": "慕课网", "url": "https://www.imooc.com"},
        "yixi": {"name": "一席", "url": "https://yixi.tv"},
        "xuetangx": {"name": "学堂在线", "url": "https://www.xuetangx.com"},
        "51zxw": {"name": "我要自学网", "url": "https://www.51zxw.net"},
        "shanbay": {"name": "扇贝单词", "url": "https://www.shanbay.com"},
        "mdn": {"name": "MDN 开发者文档", "url": "https://developer.mozilla.org"},
        "nlc": {"name": "国家图书馆公开课", "url": "https://www.nlc.cn"},
        # 扩充
        "liaoxuefeng": {"name": "廖雪峰的官方网站", "url": "https://www.liaoxuefeng.com"},
        "w3cschool": {"name": "W3Cschool", "url": "https://www.w3cschool.cn"},
        "lanqiao": {"name": "蓝桥云课", "url": "https://www.lanqiao.cn"},
        "allhistory": {"name": "全历史", "url": "https://www.allhistory.com"},
        "cdstm": {"name": "中国数字科技馆", "url": "https://www.cdstm.cn"},
        "gushiwen": {"name": "古诗文网", "url": "https://www.gushiwen.cn"},
        "shidianguji": {"name": "识典古籍", "url": "https://www.shidianguji.com"},
        "termonline": {"name": "术语在线", "url": "https://www.termonline.cn"},
        "kekenet": {"name": "可可英语", "url": "https://www.kekenet.com"},
        "doyoudo": {"name": "doyoudo", "url": "https://www.doyoudo.com"},
        "uiiiuiii": {"name": "优优教程网", "url": "https://www.uiiiuiii.com"},
        "gogoup": {"name": "站酷高高手", "url": "https://www.gogoup.com"},
        "codemao": {"name": "编程猫", "url": "https://www.codemao.cn"},
        "mdnice": {"name": "墨滴排版", "url": "https://mdnice.com"},
        "jiumodiary": {"name": "鸠摩搜书", "url": "https://www.jiumodiary.com"},
        "1nami": {"name": "1纳米学习导航", "url": "http://www.1nami.com"},
        "bijixia": {"name": "笔记侠", "url": "https://www.bijixia.net"},
        "how2j": {"name": "How2J", "url": "https://how2j.cn"},
        "cxyxiaowu": {"name": "吴师兄学算法", "url": "https://www.cxyxiaowu.com"},
        "chineselearning": {"name": "全球中文学习平台", "url": "https://www.chinese-learning.cn"},
        "xiaobaixue": {"name": "小白学编程", "url": "https://www.xiaobaixuebiancheng.com"},
    },
    "工作": {
        # 原有
        "mubu": {"name": "幕布", "url": "https://mubu.com"},
        "processon": {"name": "ProcessOn", "url": "https://www.processon.com"},
        "jianguoyun": {"name": "坚果云", "url": "https://www.jianguoyun.com"},
        "worktile": {"name": "Worktile", "url": "https://worktile.com"},
        "tower": {"name": "Tower", "url": "https://tower.im"},
        "jiandaoyun": {"name": "简道云", "url": "https://www.jiandaoyun.com"},
        "wondercv": {"name": "超级简历", "url": "https://www.wondercv.com"},
        "yuque": {"name": "语雀", "url": "https://www.yuque.com"},
        # 扩充
        "jinshuju": {"name": "金数据", "url": "https://jinshuju.com"},
        "mujicv": {"name": "木及简历", "url": "https://www.mujicv.com"},
        "jijian": {"name": "极简简历", "url": "https://www.jijian.cn"},
        "zxgj": {"name": "在线工具网", "url": "https://www.zxgj.cn"},
        "dycharts": {"name": "镝数图表", "url": "https://dycharts.com"},
        "chuangkit": {"name": "创客贴", "url": "https://www.chuangkit.com"},
        "gaoding": {"name": "稿定设计", "url": "https://www.gaoding.com"},
        "hitokoto": {"name": "一言", "url": "https://hitokoto.cn"},
        "zhixi": {"name": "知犀思维导图", "url": "https://www.zhixi.com"},
        "amymind": {"name": "AmyMind", "url": "https://amymind.com"},
        "gaituya": {"name": "改图鸭", "url": "https://www.gaituya.com"},
        "xiaohuazhuo": {"name": "小画桌", "url": "https://www.xiaohuazhuo.com"},
        "ijiaodui": {"name": "爱校对", "url": "https://www.ijiaodui.com"},
        "maoken": {"name": "猫啃网", "url": "https://www.maoken.com"},
        "photokit": {"name": "PhotoKit", "url": "https://photokit.com"},
        "doc2x": {"name": "Doc2X", "url": "https://doc2x.noedgeai.com"},
        "modao": {"name": "墨刀", "url": "https://modao.io"},
        "wjqq": {"name": "腾讯问卷", "url": "https://wj.qq.com"},
        "shimo": {"name": "石墨文档", "url": "https://shimo.im"},
        "youdaonote": {"name": "有道云笔记", "url": "https://note.youdao.com"},
        "xmind": {"name": "XMind", "url": "https://xmind.cn"},
        "dida365": {"name": "滴答清单", "url": "https://www.dida365.com"},
    },
    "娱乐": {
        # 原有
        "gcores": {"name": "机核网", "url": "https://www.gcores.com"},
        "5sing": {"name": "5sing原创音乐", "url": "https://5sing.kugou.com"},
        "xiaoyuzhou": {"name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com"},
        "acfun": {"name": "AcFun", "url": "https://www.acfun.cn"},
        "lofter": {"name": "LOFTER", "url": "https://www.lofter.com"},
        "eentry": {"name": "耳聆网", "url": "https://www.eentry.cn"},
        "bh3": {"name": "崩坏3官网", "url": "https://www.bh3.com"},
        "yangshipin": {"name": "央视频", "url": "https://www.yangshipin.cn"},
        # 扩充
        "chuapp": {"name": "触乐", "url": "https://www.chuapp.com"},
        "cowlevel": {"name": "奶牛关", "url": "https://www.cowlevel.net"},
        "cnu": {"name": "CNU视觉联盟", "url": "https://www.cnu.cc"},
        "photofans": {"name": "PhotoFans摄影网", "url": "https://bbs.photofans.cn"},
        "nyasama": {"name": "喵玉殿", "url": "https://bbs.nyasama.com"},
        "touhou": {"name": "东方幻想乡", "url": "https://bbs.touhou.cc"},
        "cbaigui": {"name": "纪妖", "url": "https://cbaigui.com"},
        "indiecn": {"name": "雀乐", "url": "https://indie.cn"},
        "deepsong": {"name": "DeepSong", "url": "https://deepsong.cn"},
        "nangua": {"name": "南瓜电影", "url": "https://nangua.movie"},
        "hanfuzhou": {"name": "汉服文化社区", "url": "https://www.hanfuzhou.com"},
        "ciweimao": {"name": "刺猬猫", "url": "https://www.ciweimao.com"},
        "boluobao": {"name": "菠萝包轻小说", "url": "https://boluobao.cc"},
        "souyun": {"name": "搜韵", "url": "https://sou-yun.cn"},
        "indienova": {"name": "IndieNova", "url": "https://indienova.com"},
        "yystv": {"name": "游戏研究社", "url": "https://yystv.cn"},
        "nga": {"name": "NGA玩家社区", "url": "https://bbs.nga.cn"},
        "moegirl": {"name": "萌娘百科", "url": "https://zh.moegirl.org.cn"},
        "coolapk": {"name": "酷安", "url": "https://www.coolapk.com"},
        "huaban": {"name": "花瓣", "url": "https://huaban.com"},
    },
    "生活": {
        # 原有
        "manmanbuy": {"name": "慢慢买", "url": "https://www.manmanbuy.com"},
        "meishij": {"name": "美食杰", "url": "https://www.meishij.net"},
        "douguo": {"name": "豆果美食", "url": "https://www.douguo.com"},
        "chunyuyisheng": {"name": "春雨医生", "url": "https://www.chunyuyisheng.com"},
        "qyer": {"name": "穷游", "url": "https://www.qyer.com"},
        "boqii": {"name": "波奇宠物", "url": "https://www.boqii.com"},
        "modian": {"name": "摩点", "url": "https://www.modian.com"},
        "weather": {"name": "中国天气网", "url": "https://www.weather.com.cn"},
        # 扩充
        "caiyunapp": {"name": "彩云天气", "url": "https://www.caiyunapp.com"},
        "qianjiapp": {"name": "钱迹记账", "url": "https://qianjiapp.com"},
        "icostapp": {"name": "iCost记账", "url": "https://www.icostapp.com"},
        "ttxn": {"name": "天天学农", "url": "https://www.ttxn.com"},
        "tahua": {"name": "踏花行", "url": "https://www.tahua.net"},
        "xiaokeai": {"name": "小可爱宠物", "url": "https://www.xiaokeai.com"},
        "lovepet": {"name": "爱宠网", "url": "https://www.lovepet.cn"},
        "pitravel": {"name": "圆周旅迹", "url": "https://pitravel.cn"},
        "mydigit": {"name": "数码之家", "url": "https://www.mydigit.cn"},
        "cntcm": {"name": "中国中医药网", "url": "https://www.cntcm.com.cn"},
        "qxbsk": {"name": "汽修帮手", "url": "https://www.qxbsk.com"},
        "ycshpon": {"name": "剩菜小助手", "url": "https://cook.yunyoujun.cn"},
        "dreamchef": {"name": "梦幻厨房", "url": "https://www.dreamchefhome.com"},
        "xiangha": {"name": "香哈菜谱", "url": "https://www.xiangha.com"},
        "fz12348": {"name": "中国法网", "url": "https://www.12348.gov.cn"},
        "cma": {"name": "中国气象数据网", "url": "https://data.cma.cn"},
        "gzweix": {"name": "精通维修下载", "url": "https://www.gzweix.com"},
        "vcxcar": {"name": "汽修工程师", "url": "https://www.vcxcar.com"},
        "xiachufang": {"name": "下厨房", "url": "https://www.xiachufang.com"},
        "boohee": {"name": "薄荷健康", "url": "https://www.boohee.com"},
        "haodf": {"name": "好大夫在线", "url": "https://www.haodf.com"},
        "familydoctor": {"name": "家庭医生在线", "url": "https://www.familydoctor.com.cn"},
    },
}

# 每天每个分类选几个网站，加起来要等于 10
CATEGORY_DISTRIBUTION = {"学习": 3, "工作": 2, "娱乐": 3, "生活": 2}