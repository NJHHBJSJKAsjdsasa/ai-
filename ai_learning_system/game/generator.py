"""
无限生成器模块
用于自动生成游戏世界中的地图、NPC、物品和妖兽
"""

import random
import uuid
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.llm_client import DescriptionGenerator
from config import get_realm_info, REALMS
from config.items import get_items_by_type, ItemType, get_item


class MapType(Enum):
    """地图类型枚举"""
    TOWN = "城镇"
    VILLAGE = "村庄"
    MOUNTAIN = "山脉"
    FOREST = "森林"
    SECRET_REALM = "秘境"
    RUINS = "遗迹"
    CAVE = "洞府"
    RIVER = "河流"
    VALLEY = "山谷"


class NPCOccupation(Enum):
    """NPC职业类型枚举"""
    SWORD_CULTIVATOR = "剑修"
    PILL_MASTER = "丹师"
    WANDERING_CULTIVATOR = "散修"
    DEMON_CULTIVATOR = "魔修"
    DEMON_BEAST = "妖修"
    TALISMAN_MASTER = "符师"
    FORMATION_MASTER = "阵法师"
    WEAPON_REFINER = "炼器师"
    MERCHANT = "商人"
    ELDER = "长老"
    DISCIPLE = "弟子"


class NPCPersonality(Enum):
    """NPC性格类型枚举"""
    ALOOF = "孤傲"
    GENTLE = "温和"
    CUNNING = "狡诈"
    RIGHTEOUS = "正直"
    COLD = "冷漠"
    ENTHUSIASTIC = "热情"
    STUBBORN = "固执"
    SLY = "圆滑"
    BRAVE = "勇猛"
    TIMID = "胆小"


class ItemRarity(Enum):
    """物品稀有度枚举"""
    COMMON = "普通"
    UNCOMMON = "优秀"
    RARE = "稀有"
    EPIC = "史诗"
    LEGENDARY = "传说"
    MYTHIC = "神话"


class MonsterType(Enum):
    """妖兽类型枚举"""
    WOLF = "狼类"
    SNAKE = "蛇类"
    BIRD = "鸟类"
    FISH = "鱼类"
    TREE_SPIRIT = "树精"
    STONE_MONSTER = "石怪"
    TIGER = "虎类"
    FOX = "狐类"
    DRAGON = "龙类"
    INSECT = "虫类"


# 中文姓氏库（500+）
SURNAMES = [
    "李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
    "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
    "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕",
    "苏", "卢", "蒋", "蔡", "贾", "丁", "魏", "薛", "叶", "阎",
    "余", "潘", "杜", "戴", "夏", "钟", "汪", "田", "任", "姜",
    "范", "方", "石", "姚", "谭", "廖", "邹", "熊", "金", "陆",
    "郝", "孔", "白", "崔", "康", "毛", "邱", "秦", "江", "史",
    "顾", "侯", "邵", "孟", "龙", "万", "段", "雷", "钱", "汤",
    "尹", "黎", "易", "常", "武", "乔", "贺", "赖", "龚", "文",
    # 复姓
    "欧阳", "太史", "端木", "上官", "司马", "东方", "独孤", "南宫",
    "万俟", "闻人", "夏侯", "诸葛", "尉迟", "公羊", "赫连", "澹台",
    "皇甫", "宗政", "濮阳", "公冶", "太叔", "申屠", "公孙", "慕容",
    "仲孙", "钟离", "长孙", "宇文", "司徒", "鲜于", "司空", "闾丘",
    "子车", "亓官", "司寇", "巫马", "公西", "颛孙", "壤驷", "公良",
    "漆雕", "乐正", "宰父", "谷梁", "拓跋", "夹谷", "轩辕", "令狐",
    "段干", "百里", "呼延", "东郭", "南门", "羊舌", "微生", "公户",
    "公玉", "公仪", "梁丘", "公仲", "公上", "公门", "公山", "公坚",
    "左丘", "公伯", "西门", "公祖", "第五", "公乘", "贯丘", "公皙",
    "南荣", "东里", "东宫", "仲长", "子书", "子桑", "即墨", "达奚",
    "褚师", "吴铭", "纳兰", "归海", "陈留", "即墨", "高阳", "高辛",
    # 更多单姓
    "安", "宝", "保", "才", "苍", "岑", "查", "柴", "车", "陈",
    "成", "迟", "仇", "储", "褚", "从", "崔", "代", "单", "党",
    "邓", "狄", "刁", "丁", "东", "冬", "董", "都", "窦", "杜",
    "端", "段", "鄂", "法", "范", "方", "房", "费", "丰", "封",
    "伏", "扶", "福", "付", "傅", "盖", "干", "甘", "高", "戈",
    "葛", "耿", "弓", "公", "宫", "巩", "贡", "勾", "古", "谷",
    "顾", "关", "官", "管", "桂", "郭", "国", "果", "哈", "海",
    "韩", "杭", "郝", "何", "和", "贺", "赫", "衡", "弘", "红",
    "侯", "后", "华", "滑", "化", "怀", "淮", "桓", "花", "黄",
    "惠", "霍", "姬", "吉", "计", "纪", "季", "贾", "简", "江",
    "姜", "蒋", "焦", "金", "晋", "靳", "荆", "井", "景", "鞠",
    "居", "康", "柯", "孔", "寇", "匡", "赖", "蓝", "郎", "劳",
    "乐", "雷", "冷", "黎", "李", "厉", "利", "郦", "连", "廉",
    "梁", "廖", "林", "凌", "刘", "柳", "龙", "娄", "卢", "鲁",
    "陆", "路", "吕", "罗", "骆", "麻", "马", "满", "毛", "茅",
    "梅", "蒙", "孟", "米", "苗", "明", "莫", "缪", "牧", "穆",
    "那", "南", "倪", "聂", "宁", "牛", "欧", "区", "潘", "庞",
    "裴", "彭", "皮", "平", "蒲", "朴", "戚", "齐", "祁", "钱",
    "乔", "秦", "丘", "邱", "裘", "曲", "屈", "全", "权", "冉",
    "饶", "任", "戎", "荣", "融", "容", "茹", "阮", "芮", "桑",
    "沙", "山", "单", "商", "尚", "韶", "邵", "申", "深", "沈",
    "盛", "施", "石", "史", "寿", "舒", "司", "斯", "宋", "苏",
    "孙", "索", "台", "太", "谈", "谭", "汤", "唐", "陶", "滕",
    "田", "童", "涂", "万", "汪", "王", "危", "韦", "卫", "尉",
    "魏", "温", "文", "闻", "翁", "乌", "巫", "吴", "伍", "武",
    "西", "席", "夏", "项", "萧", "谢", "辛", "邢", "幸", "熊",
    "徐", "许", "宣", "薛", "荀", "严", "闫", "颜", "晏", "阳",
    "杨", "仰", "养", "姚", "叶", "伊", "易", "殷", "阴", "尹",
    "印", "应", "英", "营", "尤", "游", "于", "余", "俞", "虞",
    "宇", "羽", "郁", "喻", "元", "袁", "岳", "云", "宰", "臧",
    "曾", "翟", "詹", "湛", "章", "张", "赵", "甄", "郑", "支",
    "钟", "仲", "周", "朱", "诸", "祝", "庄", "卓", "资", "子",
    "宗", "邹", "祖", "左", "佐", "冷", "凌", "聂", "宁", "庞",
]

# 中文名字库（1000+）
NAMES = [
    # 男性名字
    "伟", "强", "军", "杰", "勇", "磊", "明", "涛", "鹏", "超",
    "俊", "峰", "建", "华", "文", "斌", "刚", "辉", "宇", "浩",
    "凯", "龙", "波", "鑫", "飞", "旭", "亮", "洋", "勇", "帅",
    "雷", "宁", "博", "睿", "昊", "天", "泽", "诚", "轩", "瑞",
    "麟", "麒", "航", "逸", "晨", "辰", "昱", "晟", "烨", "煊",
    "炜", "焕", "炎", "煜", "熙", "熹", "煦", "照", "昭", "明",
    "朗", "亮", "光", "辉", "耀", "煌", "灿", "烁", "熠", "炫",
    "然", "燃", "焰", "焱", "煇", "炼", "炀", "炅", "炆", "炘",
    "秋", "秦", "程", "穆", "穰", "稷", "稹", "稼", "禾", "秀",
    "秉", "科", "秒", "秋", "秦", "程", "穆", "穰", "稷", "稹",
    "云", "霄", "霆", "霖", "霈", "霏", "霍", "霓", "霞", "霜",
    "霸", "霹", "雳", "雷", "电", "雪", "霁", "雯", "霆", "震",
    "山", "岩", "岭", "峰", "岳", "峻", "崇", "岚", "嵩", "巍",
    "川", "州", "洲", "浦", "津", "涉", "涛", "澜", "清", "源",
    "溪", "流", "河", "江", "湖", "海", "洋", "泊", "潭", "渊",
    "涵", "润", "滋", "淳", "添", "淼", "永", "泉", "淼", "冰",
    "剑", "锋", "利", "刚", "强", "勇", "武", "斌", "彬", "彦",
    "彩", "彪", "彬", "彭", "彰", "影", "形", "彦", "彦", "彦",
    "德", "行", "言", "志", "忠", "信", "义", "礼", "智", "仁",
    "孝", "悌", "廉", "耻", "勇", "毅", "恒", "韧", "坚", "卓",
    "安", "定", "宁", "静", "康", "泰", "祥", "瑞", "福", "禄",
    "寿", "喜", "乐", "欢", "悦", "怡", "愉", "畅", "舒", "适",
    "远", "达", "通", "顺", "畅", "达", "进", "升", "晋", "迁",
    "兴", "旺", "盛", "昌", "隆", "发", "财", "富", "贵", "荣",
    "华", "富", "豪", "杰", "俊", "秀", "英", "雄", "豪", "杰",
    "才", "材", "财", "裁", "采", "彩", "菜", "蔡", "仓", "苍",
    "沧", "藏", "操", "曹", "草", "册", "策", "岑", "层", "曾",
    "查", "察", "诧", "差", "柴", "豺", "禅", "馋", "缠", "蝉",
    "产", "昌", "长", "场", "尝", "常", "偿", "厂", "畅", "倡",
    "唱", "超", "抄", "钞", "焯", "朝", "潮", "吵", "炒", "车",
    "扯", "彻", "撤", "沉", "陈", "晨", "臣", "尘", "辰", "忱",
    "陈", "衬", "称", "趁", "撑", "成", "城", "诚", "承", "呈",
    # 女性名字
    "芳", "娜", "秀", "英", "敏", "静", "丽", "强", "洁", "艳",
    "娟", "霞", "玲", "燕", "梅", "丹", "萍", "红", "莉", "颖",
    "雪", "倩", "婷", "慧", "瑶", "茹", "妍", "琳", "怡", "欣",
    "悦", "彤", "雯", "岚", "菲", "萱", "蓉", "薇", "蕾", "菁",
    "梦", "琪", "琦", "瑜", "瑶", "珊", "珍", "珠", "琳", "琅",
    "琴", "瑟", "筝", "笛", "箫", "笙", "簧", "铃", "铛", "锣",
    "钗", "钿", "璎", "珞", "珊", "瑚", "琪", "琦", "瑶", "琚",
    "瑾", "瑜", "璇", "玑", "璜", "璧", "琮", "琥", "珀", "瑙",
    "珍", "珠", "琳", "琅", "玲", "珑", "珊", "瑚", "琪", "琦",
    "春", "夏", "秋", "冬", "梅", "兰", "竹", "菊", "荷", "莲",
    "桃", "李", "杏", "梨", "樱", "棠", "薇", "芷", "若", "英",
    "蓉", "芙", "蕖", "菡", "萏", "芊", "芊", "萋", "菲", "芳",
    "芬", "芳", "菲", "馥", "馨", "香", "馨", "馥", "芬", "芳",
    "月", "星", "云", "霞", "虹", "霓", "露", "霜", "雪", "冰",
    "晶", "莹", "玉", "珠", "宝", "贝", "珍", "珠", "琳", "琅",
    "婉", "娴", "淑", "慧", "贤", "惠", "贞", "静", "端", "庄",
    "秀", "丽", "美", "艳", "娇", "俏", "佳", "妙", "好", "姣",
    "思", "念", "想", "忆", "怀", "慕", "恋", "爱", "怜", "惜",
    "柔", "婉", "温", "和", "顺", "恭", "谨", "慎", "谦", "逊",
    "清", "雅", "淡", "泊", "恬", "静", "安", "宁", "幽", "寂",
    "诗", "词", "歌", "赋", "文", "章", "书", "画", "琴", "棋",
    "舞", "蹈", "歌", "唱", "吟", "咏", "诵", "读", "写", "作",
    "紫", "青", "蓝", "碧", "翠", "绿", "红", "赤", "朱", "彤",
    "素", "白", "玄", "黑", "苍", "苍", "皓", "皓", "皎", "皎",
    "冰", "清", "玉", "洁", "金", "枝", "玉", "叶", "天", "仙",
    "神", "女", "仙", "子", "妃", "嫔", "姬", "妾", "娥", "娟",
]

# 地图名称前缀
MAP_PREFIXES = {
    MapType.TOWN: ["天元", "青云", "紫霞", "金阳", "银月", "碧水", "红石", "黄沙", "白雪", "黑木"],
    MapType.VILLAGE: ["桃源", "杏花", "杨柳", "梧桐", "松柏", "竹林", "荷塘", "菊园", "梅林", "兰谷"],
    MapType.MOUNTAIN: ["昆仑", "蓬莱", "方丈", "瀛洲", "峨眉", "武当", "华山", "泰山", "衡山", "嵩山"],
    MapType.FOREST: ["迷雾", "幽暗", "古木", "苍翠", "原始", "神秘", "妖兽", "灵兽", "仙兽", "魔兽"],
    MapType.SECRET_REALM: ["九天", "天外", "虚空", "混沌", "洪荒", "太古", "远古", "上古", "中古", "近古"],
    MapType.RUINS: ["太古", "远古", "上古", "仙人", "魔神", "妖皇", "鬼帝", "修罗", "罗刹", "夜叉"],
    MapType.CAVE: ["紫云", "青霞", "金光", "银辉", "红霞", "碧波", "黄尘", "黑风", "白云", "蓝天"],
    MapType.RIVER: ["灵溪", "仙河", "神江", "龙川", "凤水", "麒麟", "玄武", "朱雀", "青龙", "白虎"],
    MapType.VALLEY: ["幽谷", "深谷", "峡谷", "山谷", "溪谷", "云谷", "雾谷", "仙谷", "灵谷", "神谷"],
}

MAP_SUFFIXES = {
    MapType.TOWN: ["城", "镇", "坊", "市", "街", "巷", "里", "坊", "邑", "郭"],
    MapType.VILLAGE: ["村", "庄", "寨", "堡", "屯", "集", "墟", "店", "铺", "驿"],
    MapType.MOUNTAIN: ["山", "岭", "峰", "岳", "峦", "崖", "巅", "顶", "脉", "系"],
    MapType.FOREST: ["林", "森", "木", "树", "丛", "莽", "原", "野", "地", "带"],
    MapType.SECRET_REALM: ["境", "界", "域", "空", "间", "府", "洞", "天", "地", "宇"],
    MapType.RUINS: ["遗址", "遗迹", "废墟", "残骸", "废墟", "古迹", "旧址", "故地", "废墟", "遗迹"],
    MapType.CAVE: ["洞", "穴", "窟", "府", "宅", "宫", "殿", "室", "阁", "楼"],
    MapType.RIVER: ["河", "江", "溪", "涧", "泉", "瀑", "潭", "湖", "泊", "池"],
    MapType.VALLEY: ["谷", "峪", "峡", "沟", "壑", "渊", "堑", "坎", "洼", "坳"],
}

# 妖兽名称前缀
MONSTER_PREFIXES = {
    MonsterType.WOLF: ["苍狼", "银狼", "血狼", "魔狼", "幽狼", "影狼", "风狼", "雷狼", "火狼", "冰狼"],
    MonsterType.SNAKE: ["蟒蛇", "毒蛇", "灵蛇", "妖蛇", "魔蛇", "玄蛇", "青蛇", "白蛇", "赤蛇", "黑蛇"],
    MonsterType.BIRD: ["灵鹰", "妖鹏", "魔鹫", "玄鸟", "青鸟", "赤鸟", "金翅", "银翼", "火凤", "冰凰"],
    MonsterType.FISH: ["灵鱼", "妖鲸", "魔鲨", "玄龟", "青龙", "赤鲤", "金鳞", "银鳍", "火鳌", "冰螭"],
    MonsterType.TREE_SPIRIT: ["古树", "妖木", "魔藤", "玄花", "青竹", "赤松", "金桂", "银梅", "火桑", "冰柏"],
    MonsterType.STONE_MONSTER: ["岩怪", "石妖", "土魔", "山精", "矿灵", "晶兽", "玉妖", "金怪", "铁魔", "铜精"],
    MonsterType.TIGER: ["猛虎", "妖虎", "魔虎", "玄虎", "青虎", "赤虎", "金虎", "银虎", "火虎", "冰虎"],
    MonsterType.FOX: ["灵狐", "妖狐", "魔狐", "玄狐", "青狐", "赤狐", "金狐", "银狐", "火狐", "冰狐"],
    MonsterType.DRAGON: ["蛟龙", "妖龙", "魔龙", "玄龙", "青龙", "赤龙", "金龙", "银龙", "火龙", "冰龙"],
    MonsterType.INSECT: ["灵虫", "妖蜂", "魔蝶", "玄蚁", "青蝉", "赤蛾", "金蜂", "银蝶", "火蚁", "冰蝉"],
}


@dataclass
class GeneratedMap:
    """生成的地图数据类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    map_type: MapType = MapType.FOREST
    level: int = 1
    size: str = "中型"
    description: str = ""
    history: str = ""
    environment: str = ""
    connections: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    monsters: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'map_type': self.map_type.value,
            'level': self.level,
            'size': self.size,
            'description': self.description,
            'history': self.history,
            'environment': self.environment,
            'connections': self.connections,
            'npcs': self.npcs,
            'monsters': self.monsters,
            'items': self.items,
        }


@dataclass
class GeneratedNPC:
    """生成的NPC数据类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    surname: str = ""
    full_name: str = ""
    gender: str = "男"
    age: int = 20
    realm_level: str = ""
    occupation: NPCOccupation = NPCOccupation.WANDERING_CULTIVATOR
    personality: NPCPersonality = NPCPersonality.GENTLE
    appearance: str = ""
    catchphrase: str = ""
    story: str = ""
    location: str = ""
    favor: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'full_name': self.full_name,
            'gender': self.gender,
            'age': self.age,
            'realm_level': self.realm_level,
            'occupation': self.occupation.value,
            'personality': self.personality.value,
            'appearance': self.appearance,
            'catchphrase': self.catchphrase,
            'story': self.story,
            'location': self.location,
            'favor': self.favor,
        }


@dataclass
class GeneratedItem:
    """生成的物品数据类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    item_type: ItemType = ItemType.MATERIAL
    rarity: ItemRarity = ItemRarity.COMMON
    attributes: Dict[str, Any] = field(default_factory=dict)
    effects: List[str] = field(default_factory=list)
    description: str = ""
    origin: str = ""
    legend: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'item_type': self.item_type.value,
            'rarity': self.rarity.value,
            'attributes': self.attributes,
            'effects': self.effects,
            'description': self.description,
            'origin': self.origin,
            'legend': self.legend,
        }


@dataclass
class GeneratedMonster:
    """生成的妖兽数据类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    monster_type: MonsterType = MonsterType.WOLF
    level: int = 1
    realm_level: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    drops: List[str] = field(default_factory=list)
    description: str = ""
    habits: str = ""
    weakness: str = ""
    location: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'monster_type': self.monster_type.value,
            'level': self.level,
            'realm_level': self.realm_level,
            'attributes': self.attributes,
            'drops': self.drops,
            'description': self.description,
            'habits': self.habits,
            'weakness': self.weakness,
            'location': self.location,
        }


class TechniqueType(Enum):
    """功法类型枚举"""
    SWORD = "剑法"
    PALM = "掌法"
    FIST = "拳法"
    FINGER = "指法"
    LEG = "腿法"
    INTERNAL = "内功"
    LIGHTNESS = "轻功"
    BODY = "炼体"
    MENTAL = "心法"
    SECRET = "秘术"


class TechniqueRarity(Enum):
    """功法稀有度枚举"""
    MORTAL = "凡阶"
    SPIRIT = "灵阶"
    EARTH = "地阶"
    HEAVEN = "天阶"
    IMMORTAL = "仙阶"


@dataclass
class GeneratedTechnique:
    """生成的功法数据类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    technique_type: TechniqueType = TechniqueType.SWORD
    rarity: TechniqueRarity = TechniqueRarity.MORTAL
    realm_required: int = 0
    description: str = ""
    effects: Dict[str, Any] = field(default_factory=dict)
    cultivation_method: str = ""
    origin: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'technique_type': self.technique_type.value,
            'rarity': self.rarity.value,
            'realm_required': self.realm_required,
            'description': self.description,
            'effects': self.effects,
            'cultivation_method': self.cultivation_method,
            'origin': self.origin,
        }


class InfiniteGenerator:
    """
    无限生成器核心类
    用于自动生成游戏世界中的各类内容
    """
    
    def __init__(self, use_llm: bool = True):
        """
        初始化无限生成器
        
        Args:
            use_llm: 是否使用LLM生成描述，默认为True
        """
        self.use_llm = use_llm
        self.description_generator = DescriptionGenerator() if use_llm else None
        
        # 初始化随机种子
        random.seed()
    
    # ==================== 基础生成方法 ====================
    
    def generate_name(self, gender: str = "random") -> Tuple[str, str, str]:
        """
        生成中文姓名
        
        Args:
            gender: 性别，"男"/"女"/"random"
            
        Returns:
            (姓氏, 名字, 全名)
        """
        surname = random.choice(SURNAMES)
        
        if gender == "random":
            gender = random.choice(["男", "女"])
        
        # 根据性别选择名字风格
        if gender == "男":
            # 男性名字倾向于使用前500个
            name = random.choice(NAMES[:500])
        else:
            # 女性名字倾向于使用后500个
            name = random.choice(NAMES[500:])
        
        full_name = f"{surname}{name}"
        return surname, name, full_name
    
    def generate_realm_level(self, target_level: int = None, variation: int = 1) -> str:
        """
        生成修为等级
        
        Args:
            target_level: 目标等级（0-8），如果为None则随机生成
            variation: 等级波动范围
            
        Returns:
            修为等级名称
        """
        if target_level is None:
            # 基于概率分布生成等级
            # 低级区域更常见
            weights = [30, 25, 20, 12, 7, 4, 1.5, 0.4, 0.1]
            level = random.choices(range(9), weights=weights)[0]
        else:
            # 在目标等级附近波动
            min_level = max(0, target_level - variation)
            max_level = min(8, target_level + variation)
            level = random.randint(min_level, max_level)
        
        realm_info = get_realm_info(level)
        return realm_info.name if realm_info else "凡人"
    
    def generate_rarity(self, target_rarity: int = None) -> ItemRarity:
        """
        生成物品稀有度
        
        Args:
            target_rarity: 目标稀有度等级（0-5），如果为None则基于概率生成
            
        Returns:
            物品稀有度枚举
        """
        if target_rarity is not None:
            return list(ItemRarity)[target_rarity]
        
        # 概率分布：普通60%，优秀20%，稀有12%，史诗5%，传说2.5%，神话0.5%
        weights = [60, 20, 12, 5, 2.5, 0.5]
        rarities = list(ItemRarity)
        return random.choices(rarities, weights=weights)[0]

    def generate_technique_rarity(self, target_rarity: int = None) -> TechniqueRarity:
        """
        生成功法稀有度

        Args:
            target_rarity: 目标稀有度等级（0-4），如果为None则基于概率生成

        Returns:
            功法稀有度枚举
        """
        if target_rarity is not None:
            return list(TechniqueRarity)[target_rarity]

        # 概率分布：凡阶50%，灵阶30%，地阶15%，天阶4%，仙阶1%
        weights = [50, 30, 15, 4, 1]
        rarities = list(TechniqueRarity)
        return random.choices(rarities, weights=weights)[0]

    # ==================== 地图生成 ====================
    
    def generate_map(self, map_type: MapType = None, target_level: int = None, 
                     connected_location: str = None) -> GeneratedMap:
        """
        生成地图
        
        Args:
            map_type: 地图类型，如果为None则随机选择
            target_level: 目标等级
            connected_location: 连接的现有地点名称
            
        Returns:
            生成的地图对象
        """
        if map_type is None:
            map_type = random.choice(list(MapType))
        
        # 生成地图名称
        prefix = random.choice(MAP_PREFIXES[map_type])
        suffix = random.choice(MAP_SUFFIXES[map_type])
        name = f"{prefix}{suffix}"
        
        # 生成等级
        if target_level is None:
            level = random.randint(1, 9)
        else:
            level = max(1, min(9, target_level + random.randint(-1, 1)))
        
        # 生成规模
        sizes = ["小型", "中型", "大型", "超大型"]
        size = random.choice(sizes)
        
        # 创建地图对象
        map_obj = GeneratedMap(
            name=name,
            map_type=map_type,
            level=level,
            size=size,
        )
        
        # 生成描述
        if self.description_generator:
            map_obj.description = self.description_generator.generate_map_description(
                map_type.value, level
            )
        else:
            map_obj.description = f"这是一处{size}的{map_type.value}，灵气缭绕，神秘莫测。"
        
        # 设置连接
        if connected_location:
            map_obj.connections.append(connected_location)
        
        return map_obj
    
    def generate_maps_batch(self, count: int, target_level: int = None) -> List[GeneratedMap]:
        """
        批量生成地图
        
        Args:
            count: 生成数量
            target_level: 目标等级
            
        Returns:
            地图对象列表
        """
        maps = []
        for _ in range(count):
            map_obj = self.generate_map(target_level=target_level)
            maps.append(map_obj)
        return maps
    
    # ==================== NPC生成 ====================
    
    def generate_npc(self, occupation: NPCOccupation = None, 
                     personality: NPCPersonality = None,
                     target_realm: str = None,
                     location: str = None) -> GeneratedNPC:
        """
        生成NPC
        
        Args:
            occupation: 职业类型
            personality: 性格类型
            target_realm: 目标修为等级
            location: 所在地点
            
        Returns:
            生成的NPC对象
        """
        # 随机性别
        gender = random.choice(["男", "女"])
        
        # 生成姓名
        surname, name, full_name = self.generate_name(gender)
        
        # 生成职业
        if occupation is None:
            occupation = random.choice(list(NPCOccupation))
        
        # 生成性格
        if personality is None:
            personality = random.choice(list(NPCPersonality))
        
        # 生成年龄（根据修为调整）
        if target_realm:
            # 根据修为等级调整年龄范围
            # target_realm 是修为名称（如"练气期"），需要找到对应的等级索引
            realm_index = 0
            for level, realm in REALMS.items():
                if realm.name == target_realm:
                    realm_index = level
                    break
            base_age = 16 + realm_index * 20
            age = random.randint(base_age, base_age + 50)
        else:
            age = random.randint(16, 300)
        
        # 生成修为
        if target_realm:
            realm_level = target_realm
        else:
            realm_level = self.generate_realm_level()
        
        # 创建NPC对象
        npc = GeneratedNPC(
            name=name,
            surname=surname,
            full_name=full_name,
            gender=gender,
            age=age,
            realm_level=realm_level,
            occupation=occupation,
            personality=personality,
            location=location or "",
        )
        
        # 生成描述
        if self.description_generator:
            npc.appearance = self.description_generator.generate_npc_description(
                full_name, occupation.value, personality.value
            )
        else:
            npc.appearance = f"{full_name}是一位{occupation.value}，性格{personality.value}，气质不凡。"
        
        # 生成口头禅
        catchphrases = {
            NPCPersonality.ALOOF: ["哼，凡人。", "不要打扰我修炼。", "你还不配与我说话。"],
            NPCPersonality.GENTLE: ["施主有礼了。", "愿道友仙途顺遂。", "相遇即是缘。"],
            NPCPersonality.CUNNING: ["嘿嘿，有好买卖吗？", "道友，我这有个消息...", "价钱好商量。"],
            NPCPersonality.RIGHTEOUS: ["邪魔外道，休得猖狂！", "正道长存！", "为了天下苍生！"],
            NPCPersonality.COLD: ["...", "有事？", "说。"],
            NPCPersonality.ENTHUSIASTIC: ["哈哈，道友你好啊！", "来来来，喝一杯！", "今日真是痛快！"],
            NPCPersonality.STUBBORN: ["我意已决！", "绝不退让！", "这是我的原则！"],
            NPCPersonality.SLY: ["这个嘛...", "或许可以商量...", "看道友的诚意了。"],
            NPCPersonality.BRAVE: ["冲啊！", "怕什么，上！", "有我在，别怕！"],
            NPCPersonality.TIMID: ["别、别伤害我...", "我、我只是路过...", "求、求道友放过..."],
        }
        npc.catchphrase = random.choice(catchphrases.get(personality, ["..."]))
        
        return npc
    
    def generate_npcs_batch(self, count: int, location: str = None, 
                            target_realm: str = None) -> List[GeneratedNPC]:
        """
        批量生成NPC
        
        Args:
            count: 生成数量
            location: 所在地点
            target_realm: 目标修为等级
            
        Returns:
            NPC对象列表
        """
        npcs = []
        for _ in range(count):
            npc = self.generate_npc(location=location, target_realm=target_realm)
            npcs.append(npc)
        return npcs
    
    # ==================== 物品生成 ====================
    
    def generate_item(self, item_type: ItemType = None, 
                      rarity: ItemRarity = None) -> GeneratedItem:
        """
        生成物品
        
        Args:
            item_type: 物品类型
            rarity: 稀有度
            
        Returns:
            生成的物品对象
        """
        if item_type is None:
            item_type = random.choice(list(ItemType))
        
        if rarity is None:
            rarity = self.generate_rarity()
        
        # 生成物品名称
        item_names = {
            ItemType.TREASURE: ["飞剑", "宝镜", "灵珠", "玉佩", "金铃", "法杖", "仙衣", "战甲"],
            ItemType.PILL: ["聚气丹", "筑基丹", "金丹", "元婴丹", "化神丹", "回春丹", "解毒丹", "增元丹"],
            ItemType.MATERIAL: ["玄铁", "精金", "灵木", "灵石", "妖核", "兽皮", "灵骨", "仙玉"],
            ItemType.BOOK: ["心法", "剑诀", "刀法", "拳谱", "身法", "阵图", "丹方", "符咒"],
            ItemType.SPIRIT_STONE: ["下品灵石", "中品灵石", "上品灵石", "极品灵石"],
            ItemType.CONSUMABLE: ["火符", "水符", "雷符", "风符", "土符", "金符", "木符", "遁符"],
        }
        
        # 确保item_type在item_names中
        if item_type not in item_names:
            # 默认使用MATERIAL类型
            item_type = ItemType.MATERIAL
        
        base_name = random.choice(item_names[item_type])
        
        # 根据稀有度添加前缀
        rarity_prefixes = {
            ItemRarity.COMMON: ["普通的", "一般的", "寻常的"],
            ItemRarity.UNCOMMON: ["精良的", "优质的", "上等的"],
            ItemRarity.RARE: ["稀有的", "珍贵的", "罕见的"],
            ItemRarity.EPIC: ["史诗的", "传奇的", "绝世的"],
            ItemRarity.LEGENDARY: ["传说的", "神话的", "太古的"],
            ItemRarity.MYTHIC: ["神话的", "至尊的", "无上的"],
        }
        
        prefix = random.choice(rarity_prefixes[rarity])
        name = f"{prefix}{base_name}"
        
        # 生成属性
        rarity_multipliers = {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 1.5,
            ItemRarity.RARE: 2.5,
            ItemRarity.EPIC: 3.5,
            ItemRarity.LEGENDARY: 5.0,
            ItemRarity.MYTHIC: 7.0,
        }
        multiplier = rarity_multipliers[rarity]
        
        attributes = {
            "power": int(random.randint(10, 50) * multiplier),
            "durability": int(random.randint(50, 100) * multiplier),
        }
        
        effects = []
        if item_type == ItemType.PILL:
            effects.append("恢复生命值")
            effects.append("恢复法力")
        elif item_type == ItemType.TREASURE:
            effects.append("攻击加成")
            effects.append("防御加成")
        elif item_type == ItemType.SPIRIT_STONE:
            effects.append("恢复法力")
            effects.append("货币")
        elif item_type == ItemType.CONSUMABLE:
            effects.append("特殊效果")
        elif item_type == ItemType.BOOK:
            effects.append("学习功法")
        elif item_type == ItemType.MATERIAL:
            effects.append("炼器材料")
            effects.append("炼丹材料")
        
        # 创建物品对象
        item = GeneratedItem(
            name=name,
            item_type=item_type,
            rarity=rarity,
            attributes=attributes,
            effects=effects,
        )
        
        # 生成描述
        if self.description_generator:
            item.description = self.description_generator.generate_item_description(
                item_type.value, rarity.value
            )
        else:
            item.description = f"这是一件{rarity.value}的{item_type.value}，散发着淡淡的灵光。"
        
        return item
    
    def generate_items_batch(self, count: int, 
                             item_type: ItemType = None) -> List[GeneratedItem]:
        """
        批量生成物品
        
        Args:
            count: 生成数量
            item_type: 物品类型
            
        Returns:
            物品对象列表
        """
        items = []
        for _ in range(count):
            item = self.generate_item(item_type=item_type)
            items.append(item)
        return items
    
    # ==================== 妖兽生成 ====================
    
    def generate_monster(self, monster_type: MonsterType = None, 
                         level: int = None,
                         location: str = None) -> GeneratedMonster:
        """
        生成妖兽
        
        Args:
            monster_type: 妖兽类型
            level: 等级
            location: 所在地点
            
        Returns:
            生成的妖兽对象
        """
        if monster_type is None:
            monster_type = random.choice(list(MonsterType))
        
        if level is None:
            level = random.randint(1, 20)
        
        # 生成名称
        prefix = random.choice(MONSTER_PREFIXES[monster_type])
        name = f"{prefix}"
        
        # 根据等级确定修为
        if level <= 3:
            realm_level = "炼气期"
        elif level <= 6:
            realm_level = "筑基期"
        elif level <= 9:
            realm_level = "金丹期"
        elif level <= 12:
            realm_level = "元婴期"
        elif level <= 15:
            realm_level = "化神期"
        elif level <= 18:
            realm_level = "炼虚期"
        else:
            realm_level = "合体期"
        
        # 生成属性
        attributes = {
            "health": level * 50,
            "attack": level * 10,
            "defense": level * 5,
            "speed": level * 3,
        }
        
        # 生成掉落物品
        drops = []
        drop_count = random.randint(0, 3)
        for _ in range(drop_count):
            item = self.generate_item()
            drops.append(item.name)
        
        # 创建妖兽对象
        monster = GeneratedMonster(
            name=name,
            monster_type=monster_type,
            level=level,
            realm_level=realm_level,
            attributes=attributes,
            drops=drops,
            location=location or "",
        )
        
        # 生成描述
        if self.description_generator:
            monster.description = self.description_generator.generate_monster_description(
                monster_type.value, level
            )
        else:
            monster.description = f"这是一只等级{level}的{monster_type.value}，妖气弥漫，凶性毕露。"
        
        # 生成习性
        habits_map = {
            MonsterType.WOLF: "群居，夜间活动，领地意识强",
            MonsterType.SNAKE: "独居，喜阴湿，擅长伏击",
            MonsterType.BIRD: "高空盘旋，视力敏锐，攻击迅猛",
            MonsterType.FISH: "水中游动，群居，受惊则散",
            MonsterType.TREE_SPIRIT: "扎根不动，感知敏锐，擅长幻术",
            MonsterType.STONE_MONSTER: "行动缓慢，防御极高，力大无穷",
            MonsterType.TIGER: "独居，领地意识极强，攻击凶猛",
            MonsterType.FOX: "狡猾多变，擅长幻术，夜间活动",
            MonsterType.DRAGON: "翱翔九天，呼风唤雨，威压惊人",
            MonsterType.INSECT: "数量众多，繁殖迅速，毒性强烈",
        }
        monster.habits = habits_map.get(monster_type, "习性不明")
        
        # 生成弱点
        weaknesses_map = {
            MonsterType.WOLF: "火属性攻击，腹部",
            MonsterType.SNAKE: "冰属性攻击，七寸",
            MonsterType.BIRD: "土属性攻击，翅膀",
            MonsterType.FISH: "雷属性攻击，离开水域",
            MonsterType.TREE_SPIRIT: "金属性攻击，火属性攻击",
            MonsterType.STONE_MONSTER: "木属性攻击，关节处",
            MonsterType.TIGER: "水属性攻击，眼睛",
            MonsterType.FOX: "雷属性攻击，尾巴",
            MonsterType.DRAGON: "特殊法宝，逆鳞",
            MonsterType.INSECT: "大范围攻击，冰冻",
        }
        monster.weakness = weaknesses_map.get(monster_type, "暂无记录")
        
        return monster
    
    def generate_monsters_batch(self, count: int, 
                                monster_type: MonsterType = None,
                                level: int = None,
                                location: str = None) -> List[GeneratedMonster]:
        """
        批量生成妖兽
        
        Args:
            count: 生成数量
            monster_type: 妖兽类型
            level: 等级
            location: 所在地点
            
        Returns:
            妖兽对象列表
        """
        monsters = []
        for _ in range(count):
            monster = self.generate_monster(
                monster_type=monster_type,
                level=level,
                location=location
            )
            monsters.append(monster)
        return monsters
    
    # ==================== 批量生成场景内容 ====================
    
    def generate_location_content(self, location_name: str, location_level: int = 1) -> Dict[str, Any]:
        """
        为地点生成完整内容（NPC、妖兽、物品）
        
        Args:
            location_name: 地点名称
            location_level: 地点等级
            
        Returns:
            包含生成内容的字典
        """
        content = {
            'npcs': [],
            'monsters': [],
            'items': [],
        }
        
        # 生成NPC（2-5个）
        npc_count = random.randint(2, 5)
        target_realm = self.generate_realm_level(location_level)
        for _ in range(npc_count):
            npc = self.generate_npc(location=location_name, target_realm=target_realm)
            content['npcs'].append(npc)
        
        # 生成妖兽（0-3个，根据地点等级）
        if location_level >= 2:  # 只有2级以上地点才有妖兽
            monster_count = random.randint(0, min(3, location_level))
            for _ in range(monster_count):
                monster = self.generate_monster(
                    level=random.randint(location_level, location_level + 3),
                    location=location_name
                )
                content['monsters'].append(monster)
        
        # 生成物品（1-4个）
        item_count = random.randint(1, 4)
        for _ in range(item_count):
            item = self.generate_item()
            content['items'].append(item)

        return content

    # ==================== 功法生成 ====================

    def generate_technique(self, technique_type: TechniqueType = None,
                          rarity: TechniqueRarity = None,
                          realm_level: int = None) -> GeneratedTechnique:
        """
        生成功法

        Args:
            technique_type: 功法类型，如果为None则随机选择
            rarity: 功法稀有度，如果为None则基于概率生成
            realm_level: 所需境界等级，如果为None则基于稀有度生成

        Returns:
            生成的功法对象
        """
        if technique_type is None:
            technique_type = random.choice(list(TechniqueType))

        if rarity is None:
            rarity = self.generate_technique_rarity()

        # 根据稀有度确定境界要求
        if realm_level is None:
            rarity_to_realm = {
                TechniqueRarity.MORTAL: random.randint(0, 2),
                TechniqueRarity.SPIRIT: random.randint(1, 4),
                TechniqueRarity.EARTH: random.randint(2, 5),
                TechniqueRarity.HEAVEN: random.randint(4, 7),
                TechniqueRarity.IMMORTAL: random.randint(7, 9),
            }
            realm_level = rarity_to_realm.get(rarity, 0)

        # 生成功法名称 - 无限生成，随机组合
        name = self._generate_unique_technique_name(technique_type)

        # 根据稀有度添加前缀
        rarity_prefixes = {
            TechniqueRarity.MORTAL: ["基础", "入门", "初级"],
            TechniqueRarity.SPIRIT: ["进阶", "中级", "精通"],
            TechniqueRarity.EARTH: ["高级", "绝世", "秘传"],
            TechniqueRarity.HEAVEN: ["天阶", "无上", "至尊"],
            TechniqueRarity.IMMORTAL: ["仙阶", "造化", "混沌"],
        }

        prefixes = rarity_prefixes.get(rarity, [""])
        prefix = random.choice(prefixes)
        if prefix:
            name = f"{prefix}{name}"

        # 生成功法效果
        effects = self._generate_technique_effects(technique_type, rarity)

        # 生成功法描述
        description = self._generate_technique_description(technique_type, rarity, name)

        # 生成修炼方法
        cultivation_method = self._generate_cultivation_method(technique_type)

        # 生成功法来源
        origins = ["上古传承", "秘境所得", "师门传授", "机缘巧合", "自创", "交易获得"]
        origin = random.choice(origins)

        technique = GeneratedTechnique(
            name=name,
            technique_type=technique_type,
            rarity=rarity,
            realm_required=realm_level,
            description=description,
            effects=effects,
            cultivation_method=cultivation_method,
            origin=origin,
        )

        return technique

    def _generate_unique_technique_name(self, technique_type: TechniqueType) -> str:
        """
        生成唯一的功法名称 - 无限生成，随机组合

        Args:
            technique_type: 功法类型

        Returns:
            唯一的功法名称
        """
        # 形容词库
        adjectives = [
            "青莲", "紫霞", "玄冰", "烈焰", "雷霆", "风暴", "暗影", "光明",
            "金刚", "琉璃", "混沌", "虚无", "星辰", "月华", "日曜", "龙吟",
            "虎啸", "凤舞", "龟息", "麒麟", "玄武", "朱雀", "白虎", "青龙",
            "天罡", "地煞", "乾坤", "阴阳", "五行", "八卦", "九宫", "十方",
            "无极", "太极", "两仪", "四象", "六合", "七星", "九天", "十地",
            "混元", "太虚", "鸿蒙", "洪荒", "太古", "远古", "上古", "中古",
            "绝世", "无双", "至尊", "无敌", "逆天", "造化", "轮回", "永恒",
            "焚天", "灭地", "裂空", "碎星", "斩月", "破日", "惊雷", "疾风",
        ]

        # 名词库 - 根据功法类型
        nouns_map = {
            TechniqueType.SWORD: ["剑诀", "剑法", "剑道", "剑意", "剑气", "剑芒", "剑罡", "剑阵"],
            TechniqueType.PALM: ["神掌", "掌法", "掌印", "掌力", "掌风", "掌劲", "掌势", "掌道"],
            TechniqueType.FIST: ["神拳", "拳法", "拳劲", "拳意", "拳道", "拳罡", "拳印", "拳风"],
            TechniqueType.FINGER: ["神指", "指法", "指劲", "指芒", "指印", "指力", "指风", "指道"],
            TechniqueType.LEG: ["神腿", "腿法", "腿劲", "腿风", "腿影", "腿罡", "腿印", "腿道"],
            TechniqueType.INTERNAL: ["神功", "真经", "心法", "秘典", "玄功", "仙诀", "道法", "奥义"],
            TechniqueType.LIGHTNESS: ["步法", "身法", "轻功", "神行", "飞遁", "瞬移", "挪移", "遁术"],
            TechniqueType.BODY: ["金身", "铁躯", "铜体", "神体", "圣体", "仙体", "魔体", "妖体"],
            TechniqueType.MENTAL: ["心经", "神念", "灵识", "神识", "魂诀", "魄法", "意念", "心神"],
            TechniqueType.SECRET: ["禁术", "秘法", "邪术", "魔功", "妖法", "鬼道", "血咒", "魂祭"],
        }

        nouns = nouns_map.get(technique_type, ["神功", "秘法", "仙诀", "道法"])

        # 后缀库
        suffixes = ["", "诀", "谱", "录", "章", "篇", "卷", "册"]

        # 随机组合生成名称
        # 组合方式1: 形容词 + 名词
        # 组合方式2: 形容词 + 形容词 + 名词
        # 组合方式3: 名词 + 后缀
        # 组合方式4: 形容词 + 名词 + 后缀

        pattern = random.choice([1, 2, 3, 4])

        if pattern == 1:
            name = f"{random.choice(adjectives)}{random.choice(nouns)}"
        elif pattern == 2:
            adj1, adj2 = random.sample(adjectives, 2)
            name = f"{adj1}{adj2}{random.choice(nouns)}"
        elif pattern == 3:
            name = f"{random.choice(nouns)}{random.choice(suffixes)}"
        else:  # pattern == 4
            name = f"{random.choice(adjectives)}{random.choice(nouns)}{random.choice(suffixes)}"

        # 添加随机数字或修饰词使其更加独特
        if random.random() < 0.3:  # 30%概率添加数字
            number = random.choice(["三", "六", "九", "十二", "十八", "二十四", "三十六", "七十二", "八十一", "一百零八", "三千", "一万"])
            name = f"{number}{name}"
        elif random.random() < 0.2:  # 20%概率添加"真"、"大"等修饰
            prefix = random.choice(["真", "大", "上", "太", "玄", "神", "圣", "仙", "魔", "妖", "鬼", "邪"])
            name = f"{prefix}{name}"

        return name

    def _generate_technique_effects(self, technique_type: TechniqueType,
                                   rarity: TechniqueRarity) -> Dict[str, Any]:
        """生成功法效果 - 使用中文键名"""
        # 基础效果值
        base_power = {
            TechniqueRarity.MORTAL: 10,
            TechniqueRarity.SPIRIT: 25,
            TechniqueRarity.EARTH: 50,
            TechniqueRarity.HEAVEN: 100,
            TechniqueRarity.IMMORTAL: 200,
        }.get(rarity, 10)

        effects = {"威力": base_power}

        # 根据功法类型添加特定效果 - 使用中文
        if technique_type == TechniqueType.SWORD:
            effects["攻击力加成"] = base_power * 2
            effects["暴击率"] = f"{base_power // 5}%"
        elif technique_type == TechniqueType.PALM:
            effects["掌力加成"] = base_power * 2
            effects["破甲"] = base_power // 3
        elif technique_type == TechniqueType.FIST:
            effects["拳劲加成"] = base_power * 2
            effects["穿透"] = base_power // 4
        elif technique_type == TechniqueType.FINGER:
            effects["指力加成"] = base_power * 2
            effects["精准"] = f"{base_power // 3}%"
        elif technique_type == TechniqueType.LEG:
            effects["腿劲加成"] = base_power * 2
            effects["连击"] = base_power // 5
        elif technique_type == TechniqueType.INTERNAL:
            effects["灵力加成"] = base_power * 3
            effects["恢复速度"] = f"+{base_power // 2}/回合"
        elif technique_type == TechniqueType.LIGHTNESS:
            effects["速度加成"] = base_power * 2
            effects["闪避率"] = f"{base_power // 3}%"
        elif technique_type == TechniqueType.BODY:
            effects["防御加成"] = base_power * 2
            effects["生命值加成"] = base_power * 5
        elif technique_type == TechniqueType.MENTAL:
            effects["神识强度"] = base_power * 2
            effects["抗性加成"] = base_power
        elif technique_type == TechniqueType.SECRET:
            effects["特殊效果"] = f"威力{base_power * 3}，但有副作用"

        return effects

    def _generate_technique_description(self, technique_type: TechniqueType,
                                       rarity: TechniqueRarity, name: str) -> str:
        """生成功法描述 - 根据名称和类型生成更丰富的描述"""

        # 从名称中提取关键词
        name_keywords = {
            "青莲": "以青莲为意，出招如莲花绽放，清雅中蕴含杀机",
            "紫霞": "吸收紫霞之气，招式绚丽多彩，如朝霞映天",
            "玄冰": "蕴含极寒之力，所到之处冰霜凝结，寒气逼人",
            "烈焰": "燃烧熊熊烈火，热力惊人，可焚尽万物",
            "雷霆": "引动天雷之力，迅捷威猛，势如奔雷",
            "风暴": "如风卷残云，攻势连绵不绝，难以抵挡",
            "暗影": "游走于阴影之中，出招诡秘难测，防不胜防",
            "光明": "正大光明，堂堂正正，以势压人",
            "金刚": "坚不可摧，如金刚护体，万法不侵",
            "琉璃": "晶莹剔透，纯净无瑕，心境通明",
            "混沌": "源自混沌初开，蕴含无穷变化，玄奥莫测",
            "虚无": "无形无相，无中生有，玄之又玄",
            "星辰": "借星辰之力，浩瀚无垠，深不可测",
            "月华": "吸收月之精华，清冷高洁，阴柔绵长",
            "日曜": "凝聚太阳真火，刚猛霸道，至阳至刚",
            "龙吟": "有龙吟之声，威震四方，气势磅礴",
            "虎啸": "如虎啸山林，威猛霸道，震慑百兽",
            "凤舞": "如凤凰起舞，优雅华丽，灵动飘逸",
            "麒麟": "蕴含麒麟瑞气，祥瑞安康，福泽绵长",
            "玄武": "如玄武镇世，防御无双，稳如泰山",
            "朱雀": "有朱雀之火，焚天煮海，热力无穷",
            "白虎": "含白虎杀伐之气，凌厉无比，所向披靡",
            "青龙": "具青龙之威，腾云驾雾，呼风唤雨",
            "天罡": "引天罡正气，刚正不阿，邪魔退避",
            "地煞": "聚地煞之气，阴狠毒辣，威力惊人",
            "乾坤": "包含乾坤之道，阴阳调和，生生不息",
            "阴阳": "融合阴阳二气，刚柔并济，变化无穷",
            "五行": "运用五行之力，相生相克，循环不息",
            "无极": "归于无极之境，返璞归真，大道至简",
            "太极": "蕴含太极真意，以柔克刚，四两拨千斤",
            "混元": "成就混元一体，万法归宗，无所不包",
            "太虚": "游于太虚之中，超脱物外，逍遥自在",
            "鸿蒙": "源自鸿蒙初判，开天辟地，造化无穷",
            "洪荒": "承载洪荒之力，古老苍茫，威能无边",
            "焚天": "有焚天之势，热力滔天，可熔金化铁",
            "灭地": "具灭地之威，山崩地裂，势不可挡",
            "裂空": "可撕裂虚空，破碎空间，神鬼莫测",
            "碎星": "能碎裂星辰，威力无穷，毁天灭地",
        }

        # 基础描述
        base_descriptions = {
            TechniqueType.SWORD: "剑法精妙，剑气纵横",
            TechniqueType.PALM: "掌法刚猛，掌风凌厉",
            TechniqueType.FIST: "拳法霸道，拳劲十足",
            TechniqueType.FINGER: "指法灵动，指劲犀利",
            TechniqueType.LEG: "腿法迅猛，腿影如风",
            TechniqueType.INTERNAL: "内功深厚，灵力充沛",
            TechniqueType.LIGHTNESS: "身法飘逸，速度惊人",
            TechniqueType.BODY: "炼体有成，肉身强横",
            TechniqueType.MENTAL: "心法玄妙，神识强大",
            TechniqueType.SECRET: "秘术诡异，威力莫测",
        }

        # 稀有度描述
        rarity_descriptions = {
            TechniqueRarity.MORTAL: "适合初学者入门修炼，循序渐进",
            TechniqueRarity.SPIRIT: "已有一定火候，修炼者可借此提升实力",
            TechniqueRarity.EARTH: "威力不凡，是难得的功法秘籍",
            TechniqueRarity.HEAVEN: "天阶功法，修炼到极致可通天彻地，成就非凡",
            TechniqueRarity.IMMORTAL: "仙阶功法，传说中仙人所创，得之可成仙问道",
        }

        # 构建描述
        # 1. 从名称中找关键词
        keyword_desc = ""
        for keyword, desc in name_keywords.items():
            if keyword in name:
                keyword_desc = desc
                break

        # 2. 基础描述
        base_desc = base_descriptions.get(technique_type, "功法玄妙")

        # 3. 稀有度描述
        rarity_desc = rarity_descriptions.get(rarity, "功法威力未知")

        # 组合描述
        if keyword_desc:
            return f"{keyword_desc}。{base_desc}，{rarity_desc}。"
        else:
            return f"{base_desc}，{rarity_desc}。"

    def _generate_cultivation_method(self, technique_type: TechniqueType) -> str:
        """生成修炼方法"""
        methods = {
            TechniqueType.SWORD: "每日练剑千次，感悟剑意。",
            TechniqueType.PALM: "对着巨石练习掌力，直至石碎。",
            TechniqueType.FIST: "打熬筋骨，拳拳用力，持之以恒。",
            TechniqueType.FINGER: "每日点戳木桩，锻炼指力。",
            TechniqueType.LEG: "负重奔跑，练习腿法。",
            TechniqueType.INTERNAL: "打坐冥想，引导灵气运行周天。",
            TechniqueType.LIGHTNESS: "在险要地形练习身法，轻身跳跃。",
            TechniqueType.BODY: "以特殊药液浸泡，锤炼肉身。",
            TechniqueType.MENTAL: "静坐冥想，排除杂念，凝练心神。",
            TechniqueType.SECRET: "需特殊条件方可修炼，谨慎为之。",
        }
        return methods.get(technique_type, "按部就班，勤加修炼。")

    def generate_techniques_batch(self, count: int = 3) -> List[GeneratedTechnique]:
        """
        批量生成功法

        Args:
            count: 生成数量

        Returns:
            功法对象列表
        """
        techniques = []
        for _ in range(count):
            technique = self.generate_technique()
            techniques.append(technique)
        return techniques


# 全局生成器实例
_default_generator: Optional[InfiniteGenerator] = None


def get_generator(use_llm: bool = True) -> InfiniteGenerator:
    """
    获取默认的无限生成器实例
    
    Args:
        use_llm: 是否使用LLM
        
    Returns:
        InfiniteGenerator实例
    """
    global _default_generator
    if _default_generator is None:
        _default_generator = InfiniteGenerator(use_llm=use_llm)
    return _default_generator


# 便捷函数
def generate_map(map_type: MapType = None, target_level: int = None) -> GeneratedMap:
    """生成地图"""
    return get_generator().generate_map(map_type, target_level)


def generate_npc(occupation: NPCOccupation = None, location: str = None) -> GeneratedNPC:
    """生成NPC"""
    return get_generator().generate_npc(occupation, location=location)


def generate_item(item_type: ItemType = None, rarity: ItemRarity = None) -> GeneratedItem:
    """生成物品"""
    return get_generator().generate_item(item_type, rarity)


def generate_monster(monster_type: MonsterType = None, level: int = None) -> GeneratedMonster:
    """生成妖兽"""
    return get_generator().generate_monster(monster_type, level)


def generate_technique(technique_type: TechniqueType = None, rarity: TechniqueRarity = None, realm_level: int = None) -> GeneratedTechnique:
    """生成功法"""
    return get_generator().generate_technique(technique_type, rarity, realm_level)


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("无限生成器测试")
    print("=" * 60)
    
    generator = InfiniteGenerator(use_llm=False)
    
    print("\n--- 测试地图生成 ---")
    for map_type in [MapType.MOUNTAIN, MapType.FOREST, MapType.TOWN]:
        map_obj = generator.generate_map(map_type=map_type, target_level=3)
        print(f"\n地图: {map_obj.name}")
        print(f"类型: {map_obj.map_type.value}")
        print(f"等级: {map_obj.level}")
        print(f"规模: {map_obj.size}")
        print(f"描述: {map_obj.description[:50]}...")
    
    print("\n--- 测试NPC生成 ---")
    for _ in range(3):
        npc = generator.generate_npc()
        print(f"\nNPC: {npc.full_name}")
        print(f"性别: {npc.gender}")
        print(f"职业: {npc.occupation.value}")
        print(f"性格: {npc.personality.value}")
        print(f"修为: {npc.realm_level}")
        print(f"口头禅: {npc.catchphrase}")
    
    print("\n--- 测试物品生成 ---")
    for rarity in [ItemRarity.COMMON, ItemRarity.RARE, ItemRarity.LEGENDARY]:
        item = generator.generate_item(rarity=rarity)
        print(f"\n物品: {item.name}")
        print(f"类型: {item.item_type.value}")
        print(f"稀有度: {item.rarity.value}")
        print(f"属性: {item.attributes}")
    
    print("\n--- 测试妖兽生成 ---")
    for monster_type in [MonsterType.WOLF, MonsterType.TIGER, MonsterType.DRAGON]:
        monster = generator.generate_monster(monster_type=monster_type, level=5)
        print(f"\n妖兽: {monster.name}")
        print(f"类型: {monster.monster_type.value}")
        print(f"等级: {monster.level}")
        print(f"修为: {monster.realm_level}")
        print(f"属性: {monster.attributes}")
        print(f"弱点: {monster.weakness}")
    
    print("\n--- 测试批量生成 ---")
    maps = generator.generate_maps_batch(3, target_level=2)
    print(f"生成了 {len(maps)} 个地图")
    for m in maps:
        print(f"  - {m.name} ({m.map_type.value})")
    
    npcs = generator.generate_npcs_batch(3, location="测试地点")
    print(f"\n生成了 {len(npcs)} 个NPC")
    for npc in npcs:
        print(f"  - {npc.full_name} ({npc.occupation.value})")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
