"""
小说数据解析器 - 从《凡人修仙传》中提取修仙数据
"""

import re
from typing import List, Dict, Set, Tuple
from pathlib import Path


class NovelParser:
    """小说解析器类"""
    
    # 预定义的小说中的关键数据（基于《凡人修仙传》已知内容）
    PREDEFINED_SECTS = {
        "七玄门": {
            "description": "由七绝上人创立，曾雄霸镜州数十载，后被挤出镜州城，搬迁至彩霞山",
            "type": "正道",
            "location": "彩霞山",
            "strength": "三流地方势力，门下弟子三四千人"
        },
        "野狼帮": {
            "description": "前身是镜州马贼，凶狠嗜血，与七玄门是死敌",
            "type": "邪道",
            "location": "镜州",
            "strength": "与七玄门抗衡的本地势力"
        },
        "黄枫谷": {
            "description": "越国七大派之一，韩立筑基后加入的门派",
            "type": "正道",
            "location": "越国",
            "strength": "越国七大派之一"
        },
        "掩月宗": {
            "description": "越国七大派之一，以女修为主",
            "type": "正道",
            "location": "越国",
            "strength": "越国七大派之一"
        },
        "清虚门": {
            "description": "越国七大派之一，道家宗门",
            "type": "正道",
            "location": "越国",
            "strength": "越国七大派之一"
        },
        "灵兽山": {
            "description": "越国七大派之一，擅长驭兽",
            "type": "正道",
            "location": "越国",
            "strength": "越国七大派之一"
        },
        "巨剑门": {
            "description": "越国七大派之一，剑修门派",
            "type": "正道",
            "location": "越国",
            "strength": "越国七大派之一"
        },
        "天阙堡": {
            "description": "越国七大派之一，以炼体著称",
            "type": "正道",
            "location": "越国",
            "strength": "越国七大派之一"
        },
        "化刀坞": {
            "description": "越国七大派之一，刀修门派",
            "type": "正道",
            "location": "越国",
            "strength": "越国七大派之一"
        }
    }
    
    PREDEFINED_TECHNIQUES = {
        "长春功": {
            "description": "木属性基础功法，韩立修仙之路的起点",
            "type": "功法",
            "element": "木",
            "realm_required": "练气期",
            "effects": ["延年益寿", "固本培元"]
        },
        "眨眼剑法": {
            "description": "墨大夫传授的凡俗剑法，以快制胜",
            "type": "武技",
            "element": "无",
            "realm_required": "凡人",
            "effects": ["剑速极快", "出其不意"]
        },
        "罗烟步": {
            "description": "轻身功法，身形如烟，难以捉摸",
            "type": "身法",
            "element": "无",
            "realm_required": "练气期",
            "effects": ["身形飘忽", "闪避提升"]
        },
        "青元剑诀": {
            "description": "韩立主修功法，可修炼至化神期",
            "type": "功法",
            "element": "木",
            "realm_required": "筑基期",
            "effects": ["剑气纵横", "威力巨大"]
        },
        "大衍决": {
            "description": "大衍神君所创，强化神识的绝世功法",
            "type": "功法",
            "element": "无",
            "realm_required": "元婴期",
            "effects": ["神识倍增", "分心多用"]
        },
        "梵圣真魔功": {
            "description": "魔界顶级功法，韩立主修功法之一",
            "type": "功法",
            "element": "魔",
            "realm_required": "化神期",
            "effects": ["肉身强化", "魔气滔天"]
        },
        "炼神术": {
            "description": "仙界禁术，可无限强化神识",
            "type": "功法",
            "element": "仙",
            "realm_required": "大乘期",
            "effects": ["神识无限增长", "逆天改命"]
        }
    }
    
    PREDEFINED_ITEMS = {
        "掌天瓶": {
            "name": "掌天瓶",
            "alias": ["小绿瓶"],
            "description": "可催熟灵药的神秘宝瓶，韩立最大的机缘",
            "type": "法宝",
            "rarity": "传说",
            "effects": ["催熟灵药", "凝聚绿液"]
        },
        "青竹蜂云剑": {
            "name": "青竹蜂云剑",
            "description": "韩立本命法宝，由万年金雷竹炼制",
            "type": "法宝",
            "rarity": "极品",
            "effects": ["辟邪神雷", "剑阵威力"]
        },
        "风雷翅": {
            "name": "风雷翅",
            "description": "雷鹏翅膀炼制，飞行速度极快",
            "type": "法宝",
            "rarity": "极品",
            "effects": ["风雷遁术", "速度无双"]
        },
        "虚天鼎": {
            "name": "虚天鼎",
            "description": "虚天殿至宝，可炼丹炼器",
            "type": "法宝",
            "rarity": "传说",
            "effects": ["炼丹增效", "炼器加成"]
        },
        "筑基丹": {
            "name": "筑基丹",
            "description": "练气期突破筑基期必备丹药",
            "type": "丹药",
            "rarity": "稀有",
            "effects": ["突破筑基", "固本培元"]
        },
        "结丹期丹药": {
            "name": "结丹期丹药",
            "description": "辅助结丹的珍贵丹药",
            "type": "丹药",
            "rarity": "稀有",
            "effects": ["辅助结丹", "提升成功率"]
        },
        "万年灵乳": {
            "name": "万年灵乳",
            "description": "可瞬间恢复法力的天地灵物",
            "type": "材料",
            "rarity": "传说",
            "effects": ["瞬间回蓝", "恢复法力"]
        },
        "金雷竹": {
            "name": "金雷竹",
            "description": "可释放辟邪神雷的珍稀灵竹",
            "type": "材料",
            "rarity": "极品",
            "effects": ["辟邪神雷", "炼制法宝"]
        }
    }
    
    PREDEFINED_CHARACTERS = {
        "韩立": {
            "alias": ["韩老魔", "二愣子", "韩跑跑"],
            "description": "主角，从山村穷小子成长为纵横三界的大能",
            "personality": "谨慎小心，善于逃跑，重情重义",
            "realm": "大乘期"
        },
        "墨大夫": {
            "alias": ["墨居仁"],
            "description": "韩立的第一个师父，教会韩立谨慎的性格",
            "personality": "老谋深算，心狠手辣",
            "realm": "凡人"
        },
        "南宫婉": {
            "alias": ["掩月宗女修"],
            "description": "韩立的道侣，掩月宗修士",
            "personality": "温婉贤淑，外柔内刚",
            "realm": "大乘期"
        },
        "大衍神君": {
            "alias": [],
            "description": "人界天才，创造出大衍决",
            "personality": "狂傲不羁，才华横溢",
            "realm": "化神期"
        }
    }
    
    PREDEFINED_TERMS = [
        "灵根", "伪灵根", "真灵根", "天灵根", "变异灵根",
        "筑基", "结丹", "元婴", "化神", "炼虚", "合体", "大乘", "渡劫",
        "法力", "神识", "神念", "灵力", "真元",
        "法宝", "法器", "灵器", "古宝", "通天灵宝",
        "丹药", "灵药", "灵草", "灵石", "灵石矿",
        "功法", "秘术", "神通", "禁制", "阵法",
        "心魔", "天劫", "心魔劫", "雷劫", "飞升",
        "储物袋", "储物戒指", "灵兽袋", "灵兽",
        "夺舍", "转世", "轮回", "因果", "机缘",
        "洞府", "秘境", "遗迹", "古修士洞府",
        "正道", "魔道", "邪道", "散修", "宗门",
        "拍卖会", "坊市", "交易会", "黑市"
    ]
    
    def __init__(self, novel_path: str = None):
        """
        初始化解析器
        
        Args:
            novel_path: 小说文件路径（可选）
        """
        self.novel_path = novel_path
        self.novel_content = ""
        
        if novel_path and Path(novel_path).exists():
            self.load_novel(novel_path)
    
    def load_novel(self, novel_path: str) -> bool:
        """
        加载小说文件
        
        Args:
            novel_path: 小说文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(novel_path, 'r', encoding='utf-8') as f:
                self.novel_content = f.read()
            return True
        except Exception as e:
            print(f"加载小说文件失败: {e}")
            return False
    
    def get_sects(self) -> Dict[str, Dict]:
        """获取门派数据"""
        return self.PREDEFINED_SECTS
    
    def get_techniques(self) -> Dict[str, Dict]:
        """获取功法数据"""
        return self.PREDEFINED_TECHNIQUES
    
    def get_items(self) -> Dict[str, Dict]:
        """获取道具数据"""
        return self.PREDEFINED_ITEMS
    
    def get_characters(self) -> Dict[str, Dict]:
        """获取角色数据"""
        return self.PREDEFINED_CHARACTERS
    
    def get_terms(self) -> List[str]:
        """获取修仙术语列表"""
        return self.PREDEFINED_TERMS
    
    def extract_from_content(self, content: str = None) -> Dict:
        """
        从小说内容中提取数据（简化版，主要使用预定义数据）
        
        Args:
            content: 小说内容，如果不提供则使用已加载的内容
            
        Returns:
            提取的数据字典
        """
        if content is None:
            content = self.novel_content
        
        if not content:
            print("警告: 没有小说内容可供解析")
            return self._get_all_predefined()
        
        # 这里可以添加更复杂的文本解析逻辑
        # 目前返回预定义数据
        return self._get_all_predefined()
    
    def _get_all_predefined(self) -> Dict:
        """获取所有预定义数据"""
        return {
            "sects": self.PREDEFINED_SECTS,
            "techniques": self.PREDEFINED_TECHNIQUES,
            "items": self.PREDEFINED_ITEMS,
            "characters": self.PREDEFINED_CHARACTERS,
            "terms": self.PREDEFINED_TERMS
        }
    
    def generate_xiuxian_terms_extension(self) -> Dict[str, str]:
        """
        生成修仙术语扩展映射
        
        Returns:
            术语映射字典
        """
        # 基于小说内容的术语映射
        term_mappings = {
            # 基础术语
            "灵根": "修仙资质",
            "伪灵根": "四属性或五属性灵根，修炼缓慢",
            "真灵根": "两属性或三属性灵根，修炼较快",
            "天灵根": "单属性灵根，修炼速度极快",
            "变异灵根": "特殊属性灵根，如雷灵根、冰灵根",
            
            # 境界术语
            "筑基": "打下修仙基础，寿命延长至两百岁",
            "结丹": "凝结金丹，寿命延长至五百岁",
            "元婴": "丹破婴生，寿命延长至千年",
            "化神": "元婴化神，可调动天地元气",
            
            # 道具术语
            "法宝": "修士炼制的宝物，威力巨大",
            "法器": "低级修士使用的器具",
            "灵器": "具有灵性的器具",
            "古宝": "上古修士留下的宝物",
            
            # 其他术语
            "夺舍": "占据他人肉身",
            "心魔": "修炼时产生的心障",
            "天劫": "突破境界时的天地考验",
            "飞升": "从下界飞升到上界"
        }
        
        return term_mappings
    
    def generate_prompt_enhancement(self) -> Dict[str, str]:
        """
        生成AI提示词增强内容
        
        Returns:
            提示词增强字典
        """
        return {
            "classic_quotes": [
                "修仙之路漫漫，唯有谨慎才能走得更远",
                "机缘天定，不可强求",
                "大道无情，修仙者当斩断凡尘",
                "宁可信其有，不可信其无",
                "留得青山在，不怕没柴烧"
            ],
            "cultivation_insights": [
                "修炼当循序渐进，不可急功近利",
                "心诚则灵，心魔自生",
                "天地灵气，取之有道",
                "功法无正邪，人心有善恶"
            ],
            "scene_descriptions": [
                "洞府深处，灵气氤氲，一株灵草正在缓缓生长",
                "拍卖会上，各路修士云集，竞价声此起彼伏",
                "秘境开启，霞光万丈，无数修士蜂拥而至",
                "天劫降临，雷霆万钧，修士咬牙苦撑"
            ]
        }


# 便捷函数
def parse_novel(novel_path: str = None) -> Dict:
    """
    解析小说文件的便捷函数
    
    Args:
        novel_path: 小说文件路径
        
    Returns:
        解析出的数据字典
    """
    parser = NovelParser(novel_path)
    return parser.extract_from_content()


def get_novel_data() -> Dict:
    """
    获取《凡人修仙传》预定义数据的便捷函数
    
    Returns:
        预定义数据字典
    """
    parser = NovelParser()
    return parser._get_all_predefined()


if __name__ == "__main__":
    # 测试解析器
    parser = NovelParser()
    
    print("=" * 60)
    print("《凡人修仙传》数据解析器测试")
    print("=" * 60)
    
    print("\n【门派数据】")
    for name, data in parser.get_sects().items():
        print(f"  {name}: {data['description'][:30]}...")
    
    print("\n【功法数据】")
    for name, data in parser.get_techniques().items():
        print(f"  {name}: {data['description'][:30]}...")
    
    print("\n【道具数据】")
    for name, data in parser.get_items().items():
        print(f"  {name}: {data['description'][:30]}...")
    
    print("\n【角色数据】")
    for name, data in parser.get_characters().items():
        print(f"  {name}: {data['description'][:30]}...")
    
    print("\n【修仙术语】")
    terms = parser.get_terms()
    print(f"  共 {len(terms)} 个术语")
    print(f"  示例: {', '.join(terms[:10])}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
