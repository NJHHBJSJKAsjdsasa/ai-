"""
NPC个性表达系统模块
实现NPC的说话风格、价值观系统和个性化表达
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


class SpeakingStyle(Enum):
    """说话风格枚举"""
    BOLD = "豪爽型"           # 语气直接、用词粗犷、常用感叹号
    ELEGANT = "文雅型"        # 用词考究、引用典故、语气平和
    GENTLE = "阴柔型"         # 语气委婉、用词细腻、含蓄表达
    COLD = "冷酷型"           # 简短直接、不带情感、命令式
    HUMOROUS = "幽默型"       # 轻松诙谐、善用比喻、开玩笑
    ARROGANT = "傲慢型"       # 居高临下、自夸、轻视他人


@dataclass
class SpeakingStyleConfig:
    """说话风格配置类"""
    style: SpeakingStyle
    name: str
    description: str
    
    # 句式特征
    sentence_patterns: List[str] = field(default_factory=list)
    
    # 常用词汇
    common_words: List[str] = field(default_factory=list)
    
    # 语气词
    modal_particles: List[str] = field(default_factory=list)
    
    # 开场白
    openings: List[str] = field(default_factory=list)
    
    # 结束语
    closings: List[str] = field(default_factory=list)
    
    # 标点偏好 (感叹号、问号、句号的使用权重)
    punctuation_weights: Dict[str, float] = field(default_factory=dict)
    
    # 句子长度偏好 (短/中/长)
    sentence_length_preference: str = "medium"
    
    # 是否使用修辞
    use_rhetoric: bool = False
    
    # 修辞类型
    rhetoric_types: List[str] = field(default_factory=list)


# 预定义的风格配置
STYLE_CONFIGS: Dict[SpeakingStyle, SpeakingStyleConfig] = {
    SpeakingStyle.BOLD: SpeakingStyleConfig(
        style=SpeakingStyle.BOLD,
        name="豪爽型",
        description="语气直接、用词粗犷、常用感叹号",
        sentence_patterns=[
            "{content}！",
            "哈哈，{content}！",
            "{content}，没问题！",
            "来！{content}！",
        ],
        common_words=[
            "痛快", "爽快", "直接", "干脆", "豪爽", "大气",
            "兄弟", "朋友", "咱们", "一起", "干", "来",
        ],
        modal_particles=["哈哈", "嘿嘿", "哟", "啊", "嘛", "咧"],
        openings=[
            "哈哈！",
            "哟！",
            "嘿！",
            "来！",
        ],
        closings=[
            "痛快！",
            "就这么定了！",
            "走着！",
        ],
        punctuation_weights={"！": 0.6, "？": 0.1, "。": 0.3},
        sentence_length_preference="short",
        use_rhetoric=False,
    ),
    
    SpeakingStyle.ELEGANT: SpeakingStyleConfig(
        style=SpeakingStyle.ELEGANT,
        name="文雅型",
        description="用词考究、引用典故、语气平和",
        sentence_patterns=[
            "{content}。",
            "古人云：'{content}'",
            "依在下之见，{content}。",
            "{content}，此乃正道也。",
        ],
        common_words=[
            "在下", "阁下", "贵客", "承蒙", "请教", "不敢",
            "之", "乎", "者", "也", "矣", "焉",
            "君子", "仁义", "礼智", "信",
        ],
        modal_particles=["也", "矣", "乎", "哉", "焉"],
        openings=[
            "久仰久仰。",
            "幸会幸会。",
            "阁下安好。",
            "在下有礼了。",
        ],
        closings=[
            "后会有期。",
            "告辞。",
            "愿君珍重。",
        ],
        punctuation_weights={"。": 0.7, "！": 0.1, "？": 0.2},
        sentence_length_preference="medium",
        use_rhetoric=True,
        rhetoric_types=["引用", "对偶", "排比"],
    ),
    
    SpeakingStyle.GENTLE: SpeakingStyleConfig(
        style=SpeakingStyle.GENTLE,
        name="阴柔型",
        description="语气委婉、用词细腻、含蓄表达",
        sentence_patterns=[
            "{content}...",
            "或许...{content}？",
            "{content}，您觉得呢？",
            "那个...{content}...",
        ],
        common_words=[
            "或许", "可能", "大概", "也许", "似乎",
            "那个", "这个", "人家", "人家觉得",
            "温柔", "细腻", "轻声", "细语",
        ],
        modal_particles=["呢", "吧", "吗", "呀", "呐", "哦"],
        openings=[
            "那个...",
            "您好...",
            "打扰一下...",
            "请问...",
        ],
        closings=[
            "再见...",
            "保重...",
            "期待再会...",
        ],
        punctuation_weights={"。": 0.4, "...": 0.3, "？": 0.2, "！": 0.1},
        sentence_length_preference="medium",
        use_rhetoric=False,
    ),
    
    SpeakingStyle.COLD: SpeakingStyleConfig(
        style=SpeakingStyle.COLD,
        name="冷酷型",
        description="简短直接、不带情感、命令式",
        sentence_patterns=[
            "{content}。",
            "{content}。",
            "{content}，不要废话。",
            "{content}，立刻。",
        ],
        common_words=[
            "执行", "完成", "结束", "开始",
            "不要", "禁止", "必须", "只能",
            "结果", "效率", "目标", "任务",
        ],
        modal_particles=[],
        openings=[
            "说。",
            "讲。",
            "何事。",
        ],
        closings=[
            "完毕。",
            "结束。",
            "走。",
        ],
        punctuation_weights={"。": 0.9, "！": 0.05, "？": 0.05},
        sentence_length_preference="short",
        use_rhetoric=False,
    ),
    
    SpeakingStyle.HUMOROUS: SpeakingStyleConfig(
        style=SpeakingStyle.HUMOROUS,
        name="幽默型",
        description="轻松诙谐、善用比喻、开玩笑",
        sentence_patterns=[
            "{content}，哈哈！",
            "{content}，就像{metaphor}一样！",
            "话说{content}...",
            "{content}，您说是不是？",
        ],
        common_words=[
            "哈哈", "嘿嘿", "呵呵", "嘻嘻",
            "话说", "那个", "这个", "咱们",
            "有趣", "好玩", "搞笑", "逗",
        ],
        modal_particles=["哈", "啦", "哟", "咧", "呗"],
        openings=[
            "哈哈，你好！",
            "哟，来了！",
            "嘿，看看谁来了！",
        ],
        closings=[
            "回头见！",
            "下次再聊！",
            "记得想我哦！",
        ],
        punctuation_weights={"！": 0.4, "~": 0.2, "。": 0.3, "？": 0.1},
        sentence_length_preference="medium",
        use_rhetoric=True,
        rhetoric_types=["比喻", "夸张", "反问"],
    ),
    
    SpeakingStyle.ARROGANT: SpeakingStyleConfig(
        style=SpeakingStyle.ARROGANT,
        name="傲慢型",
        description="居高临下、自夸、轻视他人",
        sentence_patterns=[
            "哼，{content}。",
            "{content}，这还用说？",
            "以我的身份，{content}。",
            "{content}，你懂什么？",
        ],
        common_words=[
            "本座", "本尊", "本君", "老夫",
            "区区", "蝼蚁", "凡夫", "俗子",
            "高贵", "尊贵", "超凡", "绝世",
        ],
        modal_particles=["哼", "嗤", "呵", "哈"],
        openings=[
            "哼。",
            "你来了。",
            "找本座何事？",
            "说吧。",
        ],
        closings=[
            "退下吧。",
            "去吧。",
            "不要再来烦我。",
        ],
        punctuation_weights={"。": 0.5, "！": 0.3, "？": 0.2},
        sentence_length_preference="medium",
        use_rhetoric=False,
    ),
}


@dataclass
class Values:
    """价值观数据类"""
    justice: int = 50      # 正义值 (0-100)
    interest: int = 50     # 利益值 (0-100)
    loyalty: int = 50      # 忠诚值 (0-100)
    freedom: int = 50      # 自由值 (0-100)
    power: int = 50        # 权力值 (0-100)
    
    def __post_init__(self):
        """确保所有值在0-100范围内"""
        self.justice = max(0, min(100, self.justice))
        self.interest = max(0, min(100, self.interest))
        self.loyalty = max(0, min(100, self.loyalty))
        self.freedom = max(0, min(100, self.freedom))
        self.power = max(0, min(100, self.power))
    
    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {
            "justice": self.justice,
            "interest": self.interest,
            "loyalty": self.loyalty,
            "freedom": self.freedom,
            "power": self.power,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'Values':
        """从字典创建"""
        return cls(
            justice=data.get("justice", 50),
            interest=data.get("interest", 50),
            loyalty=data.get("loyalty", 50),
            freedom=data.get("freedom", 50),
            power=data.get("power", 50),
        )


class ValuesSystem:
    """
    价值观系统类
    
    管理NPC的价值观，影响决策和行为
    """
    
    def __init__(self, values: Optional[Values] = None):
        """
        初始化价值观系统
        
        Args:
            values: 初始价值观，None则使用默认值
        """
        self.values = values if values else Values()
    
    def generate_random_values(self) -> Values:
        """
        随机生成价值观
        
        Returns:
            随机生成的价值观
        """
        # 随机生成基础值
        base_values = {
            "justice": random.randint(0, 100),
            "interest": random.randint(0, 100),
            "loyalty": random.randint(0, 100),
            "freedom": random.randint(0, 100),
            "power": random.randint(0, 100),
        }
        
        # 选择一个主导价值观，赋予更高权重
        dominant = random.choice(list(base_values.keys()))
        base_values[dominant] = random.randint(70, 100)
        
        self.values = Values(**base_values)
        return self.values
    
    def get_dominant_value(self) -> Tuple[str, int]:
        """
        获取主导价值观
        
        Returns:
            (价值观名称, 数值) 元组
        """
        values_dict = self.values.to_dict()
        dominant_name = max(values_dict, key=values_dict.get)
        dominant_value = values_dict[dominant_name]
        
        # 转换为中文名称
        name_map = {
            "justice": "正义",
            "interest": "利益",
            "loyalty": "忠诚",
            "freedom": "自由",
            "power": "权力",
        }
        
        return (name_map.get(dominant_name, dominant_name), dominant_value)
    
    def get_value_description(self) -> str:
        """
        获取价值观描述
        
        Returns:
            描述字符串
        """
        dominant_name, dominant_value = self.get_dominant_value()
        
        descriptions = {
            "正义": "正义凛然，嫉恶如仇",
            "利益": "唯利是图，精于算计",
            "忠诚": "忠心耿耿，重情重义",
            "自由": "放荡不羁，追求自在",
            "权力": "野心勃勃，渴望掌控",
        }
        
        base_desc = descriptions.get(dominant_name, "性格复杂")
        
        if dominant_value >= 80:
            intensity = "极度"
        elif dominant_value >= 60:
            intensity = "相当"
        elif dominant_value >= 40:
            intensity = "比较"
        else:
            intensity = "略微"
        
        return f"{intensity}{base_desc}"
    
    def influence_decision(self, decision: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        价值观影响决策
        
        Args:
            decision: 决策内容
            context: 决策上下文
            
        Returns:
            决策影响结果
        """
        context = context or {}
        influences = []
        
        # 根据决策类型和价值观计算影响
        decision_lower = decision.lower()
        
        # 正义型决策
        if any(word in decision_lower for word in ["帮助", "救助", "惩罚", "邪恶", "正义"]):
            justice_influence = (self.values.justice - 50) / 50  # -1 到 1
            if justice_influence > 0:
                influences.append({
                    "value": "正义",
                    "effect": "positive",
                    "strength": abs(justice_influence),
                    "reason": "符合正义价值观",
                })
            else:
                influences.append({
                    "value": "正义",
                    "effect": "negative",
                    "strength": abs(justice_influence),
                    "reason": "与正义价值观冲突",
                })
        
        # 利益型决策
        if any(word in decision_lower for word in ["交易", "赚钱", "财富", "利益", "报酬"]):
            interest_influence = (self.values.interest - 50) / 50
            if interest_influence > 0:
                influences.append({
                    "value": "利益",
                    "effect": "positive",
                    "strength": abs(interest_influence),
                    "reason": "有利可图",
                })
        
        # 忠诚型决策
        if any(word in decision_lower for word in ["朋友", "门派", "师傅", "兄弟", "承诺"]):
            loyalty_influence = (self.values.loyalty - 50) / 50
            if loyalty_influence > 0:
                influences.append({
                    "value": "忠诚",
                    "effect": "positive",
                    "strength": abs(loyalty_influence),
                    "reason": "忠于关系",
                })
        
        # 自由型决策
        if any(word in decision_lower for word in ["探索", "冒险", "离开", "独立", "游历"]):
            freedom_influence = (self.values.freedom - 50) / 50
            if freedom_influence > 0:
                influences.append({
                    "value": "自由",
                    "effect": "positive",
                    "strength": abs(freedom_influence),
                    "reason": "追求自由",
                })
        
        # 权力型决策
        if any(word in decision_lower for word in ["控制", "领导", "地位", "权力", "命令"]):
            power_influence = (self.values.power - 50) / 50
            if power_influence > 0:
                influences.append({
                    "value": "权力",
                    "effect": "positive",
                    "strength": abs(power_influence),
                    "reason": "追求权力",
                })
        
        # 计算总体倾向
        total_positive = sum(i["strength"] for i in influences if i["effect"] == "positive")
        total_negative = sum(i["strength"] for i in influences if i["effect"] == "negative")
        
        if total_positive > total_negative:
            tendency = "倾向于接受"
            tendency_score = total_positive - total_negative
        elif total_negative > total_positive:
            tendency = "倾向于拒绝"
            tendency_score = total_negative - total_positive
        else:
            tendency = "中立"
            tendency_score = 0
        
        return {
            "decision": decision,
            "influences": influences,
            "tendency": tendency,
            "tendency_score": tendency_score,
            "will_accept": tendency_score > 0.2,
        }
    
    def handle_value_conflict(self, values1: 'ValuesSystem', values2: 'ValuesSystem') -> Dict[str, Any]:
        """
        处理价值观冲突
        
        Args:
            values1: 第一个价值观系统
            values2: 第二个价值观系统
            
        Returns:
            冲突处理结果
        """
        v1 = values1.values
        v2 = values2.values
        
        # 计算各维度差异
        differences = {
            "justice": abs(v1.justice - v2.justice),
            "interest": abs(v1.interest - v2.interest),
            "loyalty": abs(v1.loyalty - v2.loyalty),
            "freedom": abs(v1.freedom - v2.freedom),
            "power": abs(v1.power - v2.power),
        }
        
        # 找出最大差异
        max_diff_name = max(differences, key=differences.get)
        max_diff_value = differences[max_diff_name]
        
        # 名称映射
        name_map = {
            "justice": "正义",
            "interest": "利益",
            "loyalty": "忠诚",
            "freedom": "自由",
            "power": "权力",
        }
        
        # 判断冲突程度
        if max_diff_value >= 60:
            conflict_level = "严重冲突"
            resolution_difficulty = "很难调和"
        elif max_diff_value >= 40:
            conflict_level = "中度冲突"
            resolution_difficulty = "需要妥协"
        elif max_diff_value >= 20:
            conflict_level = "轻度冲突"
            resolution_difficulty = "容易调和"
        else:
            conflict_level = "基本相容"
            resolution_difficulty = "无需调和"
        
        # 计算兼容性评分
        total_diff = sum(differences.values())
        compatibility = max(0, 100 - total_diff / 5)
        
        return {
            "differences": differences,
            "max_difference": (name_map[max_diff_name], max_diff_value),
            "conflict_level": conflict_level,
            "resolution_difficulty": resolution_difficulty,
            "compatibility_score": compatibility,
            "is_compatible": compatibility >= 60,
        }


class PersonalityExpression:
    """
    个性表达类
    
    实现NPC的个性化表达功能
    """
    
    # 性格到说话风格的映射
    PERSONALITY_TO_STYLE: Dict[str, SpeakingStyle] = {
        "豪爽": SpeakingStyle.BOLD,
        "直率": SpeakingStyle.BOLD,
        "粗犷": SpeakingStyle.BOLD,
        "文雅": SpeakingStyle.ELEGANT,
        "儒雅": SpeakingStyle.ELEGANT,
        "博学": SpeakingStyle.ELEGANT,
        "温柔": SpeakingStyle.GENTLE,
        "细腻": SpeakingStyle.GENTLE,
        "委婉": SpeakingStyle.GENTLE,
        "冷酷": SpeakingStyle.COLD,
        "冷漠": SpeakingStyle.COLD,
        "无情": SpeakingStyle.COLD,
        "幽默": SpeakingStyle.HUMOROUS,
        "风趣": SpeakingStyle.HUMOROUS,
        "乐观": SpeakingStyle.HUMOROUS,
        "傲慢": SpeakingStyle.ARROGANT,
        "自负": SpeakingStyle.ARROGANT,
        "高傲": SpeakingStyle.ARROGANT,
    }
    
    # 隐喻库（用于幽默风格）
    METAPHORS = [
        "猴子摘桃", "蚂蚁搬家", "蜻蜓点水", "老马识途",
        "兔子蹬鹰", "鹬蚌相争", "螳螂捕蝉", "飞蛾扑火",
        "热锅上的蚂蚁", "井底之蛙", "狐假虎威", "守株待兔",
    ]
    
    def __init__(self):
        """初始化个性表达系统"""
        self.style_configs = STYLE_CONFIGS
    
    def get_style_for_personality(self, personality: str) -> SpeakingStyle:
        """
        根据性格获取说话风格
        
        Args:
            personality: 性格描述
            
        Returns:
            说话风格
        """
        # 尝试直接匹配
        for key, style in self.PERSONALITY_TO_STYLE.items():
            if key in personality:
                return style
        
        # 默认返回文雅型
        return SpeakingStyle.ELEGANT
    
    def apply_speaking_style(
        self, 
        text: str, 
        style: SpeakingStyle,
        secondary_style: Optional[SpeakingStyle] = None,
        mix_ratio: float = 0.3
    ) -> str:
        """
        应用说话风格到文本
        
        Args:
            text: 原始文本
            style: 主要说话风格
            secondary_style: 次要说话风格（可选）
            mix_ratio: 次要风格混合比例
            
        Returns:
            风格化后的文本
        """
        config = self.style_configs.get(style)
        if not config:
            return text
        
        result = text
        
        # 应用主要风格
        result = self._apply_style_config(result, config)
        
        # 应用次要风格（混合）
        if secondary_style and secondary_style != style:
            if random.random() < mix_ratio:
                secondary_config = self.style_configs.get(secondary_style)
                if secondary_config:
                    result = self._apply_style_config(result, secondary_config, intensity=mix_ratio)
        
        return result
    
    def _apply_style_config(
        self, 
        text: str, 
        config: SpeakingStyleConfig,
        intensity: float = 1.0
    ) -> str:
        """
        应用风格配置到文本
        
        Args:
            text: 原始文本
            config: 风格配置
            intensity: 应用强度
            
        Returns:
            处理后的文本
        """
        result = text
        
        # 根据句子长度偏好调整
        if config.sentence_length_preference == "short":
            # 简化长句
            if len(result) > 20 and random.random() < intensity:
                result = result[:20] + "。"
        
        # 应用句式模板
        if config.sentence_patterns and random.random() < intensity:
            pattern = random.choice(config.sentence_patterns)
            if "{content}" in pattern:
                result = pattern.replace("{content}", result.rstrip("。！？"))
        
        # 添加语气词
        if config.modal_particles and random.random() < intensity * 0.5:
            particle = random.choice(config.modal_particles)
            result = result.rstrip("。！？") + particle + random.choice(list(config.punctuation_weights.keys()))
        
        # 应用修辞（幽默风格）
        if config.use_rhetoric and "{metaphor}" in result:
            metaphor = random.choice(self.METAPHORS)
            result = result.replace("{metaphor}", metaphor)
        
        return result
    
    def generate_greeting(
        self, 
        npc_name: str, 
        target_name: str,
        style: SpeakingStyle,
        relationship: str = "neutral"
    ) -> str:
        """
        生成个性化问候
        
        Args:
            npc_name: NPC名称
            target_name: 目标名称
            style: 说话风格
            relationship: 关系类型 (friendly/hostile/neutral)
            
        Returns:
            问候语
        """
        config = self.style_configs.get(style)
        
        greetings = {
            SpeakingStyle.BOLD: {
                "friendly": [
                    f"哈哈，{target_name}！好久不见！",
                    f"哟，{target_name}！来得正好！",
                    f"{target_name}兄弟！别来无恙啊！",
                ],
                "hostile": [
                    f"哼，{target_name}，你还敢来？",
                    f"{target_name}！找打吗？",
                ],
                "neutral": [
                    f"{target_name}，来了啊！",
                    f"哟，{target_name}，有何贵干？",
                ],
            },
            SpeakingStyle.ELEGANT: {
                "friendly": [
                    f"{target_name}阁下，别来无恙？",
                    f"久仰{target_name}阁下大名，今日得见，幸会幸会。",
                ],
                "hostile": [
                    f"{target_name}...（冷眼相视）",
                    f"阁下便是{target_name}？失敬。",
                ],
                "neutral": [
                    f"{target_name}阁下，有礼了。",
                    f"见过{target_name}阁下。",
                ],
            },
            SpeakingStyle.GENTLE: {
                "friendly": [
                    f"{target_name}...好久不见...",
                    f"{target_name}，您来了...真好...",
                ],
                "hostile": [
                    f"{target_name}...您...您怎么来了...",
                    f"那个...{target_name}...",
                ],
                "neutral": [
                    f"{target_name}...您好...",
                    f"请问...是{target_name}吗...",
                ],
            },
            SpeakingStyle.COLD: {
                "friendly": [
                    f"{target_name}。",
                    f"来了。",
                ],
                "hostile": [
                    f"{target_name}。离开。",
                    f"不欢迎你，{target_name}。",
                ],
                "neutral": [
                    f"{target_name}。",
                    f"说。",
                ],
            },
            SpeakingStyle.HUMOROUS: {
                "friendly": [
                    f"哈哈，{target_name}！想死我了！",
                    f"哟，这不是{target_name}吗！来得正好！",
                ],
                "hostile": [
                    f"哎呀，{target_name}，什么风把您吹来了？",
                    f"{target_name}？稀客稀客！",
                ],
                "neutral": [
                    f"嘿，{target_name}！",
                    f"{target_name}，好久不见！",
                ],
            },
            SpeakingStyle.ARROGANT: {
                "friendly": [
                    f"{target_name}，你来了。",
                    f"哼，{target_name}，还算准时。",
                ],
                "hostile": [
                    f"{target_name}，跪下。",
                    f"蝼蚁{target_name}，找本座何事？",
                ],
                "neutral": [
                    f"{target_name}，说吧。",
                    f"{target_name}，何事？",
                ],
            },
        }
        
        style_greetings = greetings.get(style, greetings[SpeakingStyle.ELEGANT])
        relationship_greetings = style_greetings.get(relationship, style_greetings["neutral"])
        
        return random.choice(relationship_greetings)
    
    def generate_dialogue(
        self, 
        npc_name: str,
        context: Dict[str, Any],
        style: SpeakingStyle
    ) -> str:
        """
        生成个性化对话
        
        Args:
            npc_name: NPC名称
            context: 对话上下文
            style: 说话风格
            
        Returns:
            对话内容
        """
        topic = context.get("topic", "general")
        location = context.get("location", "")
        mood = context.get("mood", "neutral")
        
        # 根据话题生成基础内容
        base_content = self._generate_base_dialogue(topic, location, mood)
        
        # 应用风格
        styled_content = self.apply_speaking_style(base_content, style)
        
        return styled_content
    
    def _generate_base_dialogue(self, topic: str, location: str, mood: str) -> str:
        """
        生成基础对话内容
        
        Args:
            topic: 话题
            location: 地点
            mood: 心情
            
        Returns:
            基础对话内容
        """
        dialogues = {
            "general": [
                "今日天气不错。",
                "修仙之路漫漫。",
                "道友有何指教？",
            ],
            "cultivation": [
                "修炼需持之以恒。",
                "境界突破需要机缘。",
                "心法修炼不可急躁。",
            ],
            "trade": [
                "这件物品如何？",
                "价格可以商量。",
                "公平交易，童叟无欺。",
            ],
            "quest": [
                "此事颇为棘手。",
                "需要一些时间。",
                "报酬如何？",
            ],
            "combat": [
                "来战！",
                "请赐教。",
                "小心了。",
            ],
        }
        
        topic_dialogues = dialogues.get(topic, dialogues["general"])
        
        # 根据心情调整
        if mood == "happy":
            topic_dialogues = [d + "（微笑）" for d in topic_dialogues]
        elif mood == "angry":
            topic_dialogues = [d + "（怒）" for d in topic_dialogues]
        
        return random.choice(topic_dialogues)
    
    def generate_thought(
        self, 
        npc_name: str,
        situation: Dict[str, Any],
        values: Optional[Values] = None
    ) -> str:
        """
        生成内心想法
        
        Args:
            npc_name: NPC名称
            situation: 情境描述
            values: 价值观（影响想法）
            
        Returns:
            内心想法
        """
        situation_type = situation.get("type", "general")
        target = situation.get("target", "")
        
        # 基础想法模板
        thought_templates = {
            "general": [
                "今天又是平凡的一天...",
                "修仙之路，何时才能有所成就？",
                "该去修炼了...",
            ],
            "meeting": [
                f"{target}...此人给我一种奇怪的感觉...",
                f"{target}看起来不简单...",
                f"要小心{target}...",
            ],
            "combat": [
                "这一战必须赢！",
                "对手很强，不能大意。",
                "找机会撤退...",
            ],
            "trade": [
                "这笔交易划算吗？",
                "能不能再压低价格？",
                "这东西值这个价吗？",
            ],
            "discovery": [
                "这是...机缘？",
                "要小心，可能有危险。",
                "不能让别人发现...",
            ],
        }
        
        thoughts = thought_templates.get(situation_type, thought_templates["general"])
        thought = random.choice(thoughts)
        
        # 根据价值观调整
        if values:
            if values.justice > 70 and situation_type == "combat":
                thought = "为了正义，这一战不可避免！"
            elif values.interest > 70 and situation_type == "trade":
                thought = "一定要争取到最大利益！"
            elif values.loyalty > 70 and situation_type == "meeting":
                thought = f"{target}是可信之人..."
            elif values.freedom > 70 and situation_type == "general":
                thought = "何时才能自由自在，不受束缚？"
            elif values.power > 70 and situation_type == "discovery":
                thought = "这能让我变得更强！"
        
        return f"【内心】{thought}"
    
    def format_speech(
        self, 
        npc_name: str, 
        content: str,
        style: SpeakingStyle,
        add_quote: bool = True
    ) -> str:
        """
        格式化说话内容
        
        Args:
            npc_name: NPC名称
            content: 说话内容
            style: 说话风格
            add_quote: 是否添加引号
            
        Returns:
            格式化后的内容
        """
        config = self.style_configs.get(style)
        
        # 应用风格
        styled_content = self.apply_speaking_style(content, style)
        
        # 添加引号
        if add_quote:
            styled_content = f"「{styled_content}」"
        
        # 添加说话人
        formatted = f"{npc_name}：{styled_content}"
        
        return formatted
    
    def generate_mixed_style(
        self,
        primary_style: SpeakingStyle,
        secondary_style: SpeakingStyle,
        mix_ratio: float = 0.3
    ) -> SpeakingStyle:
        """
        生成混合风格
        
        Args:
            primary_style: 主风格
            secondary_style: 次风格
            mix_ratio: 混合比例
            
        Returns:
            混合后的风格（返回主风格，但标记了混合信息）
        """
        # 这里可以创建一个新的混合风格配置
        # 简化处理：返回主风格，但在应用时会使用混合比例
        return primary_style
    
    def get_style_description(self, style: SpeakingStyle) -> str:
        """
        获取风格描述
        
        Args:
            style: 说话风格
            
        Returns:
            描述字符串
        """
        config = self.style_configs.get(style)
        if config:
            return f"{config.name} - {config.description}"
        return "未知风格"


# 全局实例
personality_expression = PersonalityExpression()


def get_personality_expression() -> PersonalityExpression:
    """
    获取全局个性表达实例
    
    Returns:
        PersonalityExpression实例
    """
    return personality_expression


# 便捷函数
def apply_style(text: str, style: SpeakingStyle) -> str:
    """
    便捷函数：应用说话风格
    
    Args:
        text: 文本
        style: 风格
        
    Returns:
        风格化文本
    """
    return personality_expression.apply_speaking_style(text, style)


def generate_npc_greeting(
    npc_name: str,
    target_name: str,
    personality: str,
    relationship: str = "neutral"
) -> str:
    """
    便捷函数：生成NPC问候
    
    Args:
        npc_name: NPC名称
        target_name: 目标名称
        personality: 性格
        relationship: 关系
        
    Returns:
        问候语
    """
    style = personality_expression.get_style_for_personality(personality)
    return personality_expression.generate_greeting(npc_name, target_name, style, relationship)
