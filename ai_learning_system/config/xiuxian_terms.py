"""
修仙术语映射模块
将现代术语映射到修仙术语
"""

from typing import Dict, Optional

# 修仙术语映射字典
XIUXIAN_TERMS: Dict[str, list] = {
    # 系统相关
    "记忆": ["神识", "记忆玉简", "灵识印记"],
    "学习": ["悟道", "修炼", "参悟"],
    "帮助": ["指点", "解惑", "传道"],
    "存储": ["封印", "铭刻", "刻录"],
    "删除": ["消散", "湮灭", "抹去"],
    "数据": ["天机", "道韵", "玄奥"],
    "信息": ["讯息", "情报", "消息"],
    "记录": ["记载", "笔录", "典籍"],
    
    # 角色相关
    "用户": ["道友", "小友", "道兄"],
    "玩家": ["道友", "小友", "修士"],
    "AI": ["贫道", "本座", "老夫"],
    "NPC": ["道友", "前辈", "高人"],
    "助手": ["道童", "侍从", "护法"],
    "主人": ["师尊", "前辈", "恩公"],
    
    # 属性相关
    "经验": ["修为", "道行", "功力"],
    "等级": ["境界", "层数", "阶位"],
    "生命值": ["气血", "生机", "命元"],
    "魔法值": ["灵力", "真元", "法力"],
    "体力": ["元气", "精气", "体力"],
    "金币": ["灵石", "仙玉", "灵晶"],
    "货币": ["灵石", "仙玉", "财物"],
    "装备": ["法宝", "灵器", "法器"],
    "物品": ["灵物", "宝物", "物件"],
    
    # 游戏相关
    "游戏": ["修仙", "问道", "修行"],
    "开始": ["启程", "出发", "动身"],
    "结束": ["终结", "落幕", "归寂"],
    "胜利": ["飞升", "成仙", "得道"],
    "失败": ["陨落", "身死", "道消"],
    "战斗": ["斗法", "交手", "比试"],
    "攻击": ["出击", "施法", "出招"],
    "防御": ["抵挡", "防御", "护体"],
    "技能": ["法术", "神通", "道法"],
    "任务": ["使命", "委托", "事宜"],
    
    # 时间相关
    "时间": ["光阴", "岁月", "时日"],
    "天": ["日", "天", "昼夜"],
    "年": ["载", "岁", "春秋"],
    "速度": ["神速", "迅捷", "快慢"],
    
    # 地点相关
    "地图": ["疆域", "领地", "区域"],
    "城市": ["城池", "仙城", "坊市"],
    "村庄": ["村落", "山寨", "洞府"],
    "家": ["洞府", "居所", "住处"],
    "商店": ["店铺", "商行", "摊位"],
    
    # 动作相关
    "看": ["观", "察", "视"],
    "走": ["行", "奔", "驰"],
    "说": ["言", "语", "道"],
    "想": ["思", "念", "悟"],
    "吃": ["食", "服用", "炼化"],
    "喝": ["饮", "啜", "服"],
    "拿": ["取", "持", "握"],
    "给": ["赠", "送", "赐"],
    
    # 状态相关
    "好": ["善", "佳", "良"],
    "坏": ["恶", "劣", "差"],
    "强": ["强", "厉害", "高强"],
    "弱": ["弱", "弱小", "微弱"],
    "快": ["快", "迅", "疾"],
    "慢": ["慢", "缓", "迟"],
    
    # 其他
    "名字": ["名号", "称谓", "道号"],
    "你好": ["道友有礼", "见过道友", "久仰"],
    "谢谢": ["多谢", "感激", "铭记"],
    "再见": ["告辞", "后会有期", "珍重"],
    "是": ["然", "善", "可"],
    "否": ["非也", "不然", "不可"],
    "不知道": ["不知", "未晓", "不明"],
    "明白": ["明了", "知晓", "清楚"],
    "问题": ["疑问", "困惑", "难题"],
    "答案": ["解答", "答复", "回应"],
}

# 反向映射（修仙术语到现代术语）
REVERSE_TERMS: Dict[str, str] = {}
for modern, xiuxian_list in XIUXIAN_TERMS.items():
    for xiuxian in xiuxian_list:
        if xiuxian not in REVERSE_TERMS:
            REVERSE_TERMS[xiuxian] = modern


def modern_to_xiuxian(text: str, context: Optional[str] = None) -> str:
    """
    将现代术语转换为修仙术语
    
    Args:
        text: 要转换的文本
        context: 上下文，用于选择最合适的术语
        
    Returns:
        转换后的文本
    """
    result = text
    for modern, xiuxian_list in XIUXIAN_TERMS.items():
        if modern in result:
            # 根据上下文选择最合适的术语，默认选择第一个
            xiuxian = xiuxian_list[0]
            result = result.replace(modern, xiuxian)
    return result


def xiuxian_to_modern(text: str) -> str:
    """
    将修仙术语转换为现代术语
    
    Args:
        text: 要转换的文本
        
    Returns:
        转换后的文本
    """
    result = text
    for xiuxian, modern in REVERSE_TERMS.items():
        if xiuxian in result:
            result = result.replace(xiuxian, modern)
    return result


def get_xiuxian_term(modern_term: str, index: int = 0) -> str:
    """
    获取指定现代术语对应的修仙术语
    
    Args:
        modern_term: 现代术语
        index: 修仙术语列表的索引，默认为0
        
    Returns:
        修仙术语，如果不存在则返回原术语
    """
    if modern_term in XIUXIAN_TERMS:
        terms = XIUXIAN_TERMS[modern_term]
        if index < len(terms):
            return terms[index]
        return terms[0]
    return modern_term


# 常用短语模板
XIUXIAN_PHRASES = {
    "greeting": [
        "道友有礼了，贫道这厢有礼。",
        "见过道友，久仰大名。",
        "道友安好，今日有缘相见。",
        "贫道在此恭候道友多时。",
    ],
    "confirm": [
        "善。",
        "可。",
        "然也。",
        "正该如此。",
        "大善。",
    ],
    "deny": [
        "非也。",
        "不可。",
        "不然。",
        "此事不妥。",
        "恕难从命。",
    ],
    "ask": [
        "道友此问，触及大道...",
        "此事玄妙，容贫道思量...",
        "道友所问，正是修仙之要...",
        "此乃天机，本不该泄露...",
    ],
    "unknown": [
        "此事玄妙，贫道亦需参悟...",
        "天机难测，贫道也不甚明了。",
        "道友所问，超出了贫道的认知。",
        "待贫道闭关参悟后再答复道友。",
    ],
    "cultivation": [
        "道友修炼有成，可喜可贺。",
        "修为精进，离大道又近一步。",
        "勤加修炼，必有所成。",
        "修仙之路漫漫，需持之以恒。",
    ],
    "breakthrough": [
        "恭喜道友突破成功，修为更上一层楼！",
        "突破瓶颈，道行大进！",
        "天助道友，突破成功！",
        "苦修终有回报，恭喜突破！",
    ],
    "death": [
        "道友寿元已尽，魂归天地...",
        "身死道消，令人惋惜...",
        "轮回转世，来世再续仙缘...",
        "大道无情，道友一路走好...",
    ],
}


def get_phrase(phrase_type: str, index: Optional[int] = None) -> str:
    """
    获取修仙风格短语
    
    Args:
        phrase_type: 短语类型
        index: 索引，如果为None则随机返回
        
    Returns:
        修仙风格短语
    """
    import random
    
    if phrase_type in XIUXIAN_PHRASES:
        phrases = XIUXIAN_PHRASES[phrase_type]
        if index is not None and index < len(phrases):
            return phrases[index]
        return random.choice(phrases)
    return ""
