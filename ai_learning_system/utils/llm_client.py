"""
本地LLM客户端模块
用于集成本地小模型(ollama)生成修仙风格的描述
"""

import requests
import logging
from typing import Optional, Dict, Any
import time

# 配置日志
logger = logging.getLogger(__name__)


class LocalLLM:
    """
    本地LLM客户端类
    用于与Ollama本地模型服务进行交互
    """

    def __init__(self, model: str = "qwen2.5:3b", base_url: str = "http://localhost:11434"):
        """
        初始化本地LLM客户端

        Args:
            model: 模型名称，默认为 qwen2.5:3b
            base_url: Ollama服务地址，默认为 http://localhost:11434
        """
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/generate"
        self._available = None  # 缓存可用性检查结果

    def is_available(self) -> bool:
        """
        检查Ollama服务是否可用

        Returns:
            bool: 服务是否可用
        """
        # 如果已缓存结果，直接返回
        if self._available is not None:
            return self._available

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            self._available = response.status_code == 200
            if self._available:
                logger.info(f"Ollama服务可用，模型: {self.model}")
            else:
                logger.warning(f"Ollama服务返回状态码: {response.status_code}")
            return self._available
        except requests.exceptions.ConnectionError:
            logger.warning("无法连接到Ollama服务，请确保Ollama已启动")
            self._available = False
            return False
        except requests.exceptions.Timeout:
            logger.warning("连接Ollama服务超时")
            self._available = False
            return False
        except Exception as e:
            logger.warning(f"检查Ollama服务时出错: {e}")
            self._available = False
            return False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9,
        retry_count: int = 2
    ) -> str:
        """
        调用Ollama生成文本

        Args:
            prompt: 输入提示词
            max_tokens: 最大生成token数
            temperature: 温度参数，控制随机性
            top_p: 核采样参数
            retry_count: 失败重试次数

        Returns:
            str: 生成的文本，如果失败则返回空字符串
        """
        if not self.is_available():
            logger.warning("Ollama服务不可用，无法生成文本")
            return ""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }
        }

        for attempt in range(retry_count + 1):
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                generated_text = result.get("response", "").strip()
                logger.debug(f"成功生成文本，长度: {len(generated_text)}")
                return generated_text
            except requests.exceptions.Timeout:
                logger.warning(f"生成请求超时 (尝试 {attempt + 1}/{retry_count + 1})")
                if attempt < retry_count:
                    time.sleep(1)
                    continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"生成请求失败 (尝试 {attempt + 1}/{retry_count + 1}): {e}")
                if attempt < retry_count:
                    time.sleep(1)
                    continue
            except Exception as e:
                logger.error(f"生成文本时发生错误: {e}")
                break

        return ""

    def generate_with_fallback(
        self,
        prompt: str,
        fallback: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        生成文本，如果失败则返回备用内容

        Args:
            prompt: 输入提示词
            fallback: 备用内容
            max_tokens: 最大生成token数
            temperature: 温度参数

        Returns:
            str: 生成的文本或备用内容
        """
        result = self.generate(prompt, max_tokens, temperature)
        return result if result else fallback


class PromptTemplates:
    """
    提示词模板类
    提供修仙/武侠风格的描述生成提示词
    """

    # 修仙风格描述要素
    XIUXIAN_ELEMENTS = {
        "atmosphere": [
            "灵气浓郁", "云雾缭绕", "仙气氤氲", "霞光万道", "瑞气千条",
            "阴风阵阵", "煞气弥漫", "魔气滔天", "妖气冲天", "死气沉沉"
        ],
        "history": [
            "上古遗迹", "远古战场", "仙人洞府", "魔道圣地", "妖族领地",
            "宗门旧址", "秘境入口", "禁地深处", "天外天", "九幽之地"
        ],
        "appearance": [
            "仙风道骨", "鹤发童颜", "面容俊朗", "气质出尘", "威压惊人",
            "妖异俊美", "狰狞可怖", "慈眉善目", "冷峻孤傲", "温润如玉"
        ],
        "aura": [
            "金丹期", "元婴期", "化神期", "炼虚期", "合体期",
            "大乘期", "渡劫期", "真仙", "金仙", "太乙金仙"
        ]
    }

    @staticmethod
    def generate_map_description(map_type: str, level: int) -> str:
        """
        生成地图描述提示词

        Args:
            map_type: 地图类型，如"山脉", "森林", "洞府"等
            level: 地图等级，影响危险程度和资源丰富度

        Returns:
            str: 完整的提示词
        """
        danger_level = "低" if level < 3 else "中" if level < 6 else "高" if level < 9 else "极高"
        resource_level = "稀少" if level < 3 else "一般" if level < 6 else "丰富" if level < 9 else "极其丰富"

        prompt = f"""请用中文生成一段修仙风格的{map_type}场景描述。

要求：
1. 使用修仙/武侠风格的中文描述
2. 包含环境氛围、灵气浓度、历史传说等要素
3. 危险等级：{danger_level}，资源等级：{resource_level}
4. 描述长度在100-200字之间
5. 语言要优美、有画面感

请直接输出描述内容，不要添加标题或额外说明。"""

        return prompt

    @staticmethod
    def generate_npc_description(name: str, occupation: str, personality: str) -> str:
        """
        生成NPC描述提示词

        Args:
            name: NPC姓名
            occupation: NPC职业，如"剑修", "丹师", "散修"等
            personality: NPC性格，如"孤傲", "温和", "狡诈"等

        Returns:
            str: 完整的提示词
        """
        prompt = f"""请用中文生成一段修仙风格的NPC角色描述。

角色信息：
- 姓名：{name}
- 身份：{occupation}
- 性格：{personality}

要求：
1. 使用修仙/武侠风格的中文描述
2. 包含外貌特征、气质、穿着、修为气息等要素
3. 描述要符合角色的身份和性格
4. 描述长度在80-150字之间
5. 语言要有画面感和代入感

请直接输出描述内容，不要添加标题或额外说明。"""

        return prompt

    @staticmethod
    def generate_item_description(item_type: str, rarity: str) -> str:
        """
        生成物品描述提示词

        Args:
            item_type: 物品类型，如"法宝", "丹药", "灵草"等
            rarity: 稀有度，如"普通", "稀有", "传说"等

        Returns:
            str: 完整的提示词
        """
        prompt = f"""请用中文生成一段修仙风格的{item_type}物品描述。

物品信息：
- 类型：{item_type}
- 稀有度：{rarity}

要求：
1. 使用修仙/武侠风格的中文描述
2. 包含外观、材质、灵气波动、来历传说等要素
3. 描述要符合物品的稀有度和类型
4. 描述长度在60-120字之间
5. 语言要有神秘感和吸引力

请直接输出描述内容，不要添加标题或额外说明。"""

        return prompt

    @staticmethod
    def generate_monster_description(monster_type: str, level: int) -> str:
        """
        生成妖兽描述提示词

        Args:
            monster_type: 妖兽类型，如"虎妖", "蛇精", "魔龙"等
            level: 妖兽等级

        Returns:
            str: 完整的提示词
        """
        cultivation_level = "炼气期" if level < 3 else "筑基期" if level < 6 else "金丹期" if level < 9 else "元婴期" if level < 12 else "化神期"
        threat_level = "低" if level < 3 else "中" if level < 6 else "高" if level < 9 else "极高"

        prompt = f"""请用中文生成一段修仙风格的妖兽描述。

妖兽信息：
- 种类：{monster_type}
- 修为：{cultivation_level}
- 威胁等级：{threat_level}

要求：
1. 使用修仙/武侠风格的中文描述
2. 包含外形特征、妖气、能力特点、栖息环境等要素
3. 描述要符合妖兽的修为等级和威胁程度
4. 描述长度在80-150字之间
5. 语言要有威慑力和神秘感

请直接输出描述内容，不要添加标题或额外说明。"""

        return prompt

    @staticmethod
    def generate_cultivation_breakthrough_description(realm: str, success: bool) -> str:
        """
        生成突破境界描述提示词

        Args:
            realm: 目标境界
            success: 是否突破成功

        Returns:
            str: 完整的提示词
        """
        result = "成功突破" if success else "突破失败"
        prompt = f"""请用中文生成一段修仙风格的境界突破描述。

突破信息：
- 目标境界：{realm}
- 结果：{result}

要求：
1. 使用修仙/武侠风格的中文描述
2. 包含天地异象、体内变化、心境感受等要素
3. 描述要符合突破结果（成功或失败）
4. 描述长度在100-180字之间
5. 语言要有气势和感染力

请直接输出描述内容，不要添加标题或额外说明。"""

        return prompt


class DescriptionGenerator:
    """
    描述生成器类
    整合LocalLLM和PromptTemplates，提供带备用机制的描述生成
    """

    # 默认描述模板
    DEFAULT_DESCRIPTIONS = {
        "map": {
            "山脉": "此处群山连绵，灵气充沛，云雾缭绕间隐约可见仙鹤翱翔。相传上古时期有仙人在此悟道，留下诸多遗迹。山中妖兽横行，却也孕育着无数天材地宝。",
            "森林": "古木参天，遮天蔽日，林中灵气氤氲，奇花异草遍地。传闻深处有千年妖兽盘踞，亦有上古修士留下的洞府秘境。",
            "洞府": "石室幽深，四壁刻满古老符文，散发着淡淡的灵光。空气中弥漫着丹药的清香，显然曾有高人在此修行炼丹。",
            "城池": "仙城巍峨，琼楼玉宇鳞次栉比。街道上车水马龙，修士往来穿梭，店铺林立，售卖各种灵丹妙药、法宝符箓。",
            "河流": "灵河蜿蜒，水面波光粼粼，水中蕴含着浓郁的灵气。河岸两边灵草丰茂，时常有修士在此采集灵药、洗涤法宝。",
        },
        "npc": {
            "剑修": "一袭白衣，背负长剑，周身剑气缭绕。目光如电，眉宇间透着一股凌厉之气，显然是一位剑道高手。",
            "丹师": "身着青色道袍，腰间悬挂着紫金葫芦，手中把玩着一枚灵丹。面容慈祥，眼神中透着睿智，浑身散发着淡淡的药香。",
            "散修": "衣衫朴素，但气质不凡，眼中闪烁着精明之色。虽无宗门背景，却有一股坚韧不拔的意志。",
            "魔修": "黑袍加身，周身魔气缭绕，眼神阴鸷。举手投足间散发着危险的气息，令人不寒而栗。",
            "妖修": "半人半妖，保留了部分妖族特征，眼神中既有野兽的凶性，又有人类的狡黠。",
        },
        "item": {
            "法宝": "通体晶莹剔透，散发着柔和的光芒，表面刻满了玄奥的符文。握在手中能感受到其中蕴含的强大灵力。",
            "丹药": "圆润如玉，散发着沁人心脾的药香，表面有淡淡的丹纹流转。服用后可增进修为，疗伤治病。",
            "灵草": "叶片翠绿欲滴，顶端开着一朵晶莹剔透的小花，散发着浓郁的灵气。是炼制高阶丹药的珍贵材料。",
            "功法": "古朴的玉简上记载着玄奥的修炼法门，神识探入其中，能感受到其中蕴含的大道至理。",
            "材料": "质地坚硬，表面有着天然的纹理，蕴含着浓郁的灵气。是炼制法宝的绝佳材料。",
        },
        "monster": {
            "虎妖": "体型庞大，毛发如钢针般竖立，双眼泛着幽绿的光芒。口中獠牙锋利，周身妖气冲天，一声咆哮震得山林颤抖。",
            "蛇精": "身躯蜿蜒数十丈，鳞片闪烁着寒光，吐着猩红的信子。眼中透着阴冷和狡诈，毒液可腐蚀金石。",
            "魔龙": "龙躯横亘天际，黑焰缭绕，龙威浩荡。一双龙目如灯笼般巨大，俯视众生如蝼蚁。",
            "狐妖": "九条尾巴摇曳生姿，眼波流转间媚态横生。看似柔弱，实则妖法高深，擅长幻术迷惑人心。",
            "狼妖": "群狼环伺，头狼体型巨大，毛发银白。眼神凶狠，獠牙外露，行动如风，配合默契。",
        }
    }

    def __init__(self, model: str = "qwen2.5:3b", base_url: str = "http://localhost:11434"):
        """
        初始化描述生成器

        Args:
            model: 模型名称
            base_url: Ollama服务地址
        """
        self.llm = LocalLLM(model=model, base_url=base_url)
        self.templates = PromptTemplates()
        self._use_llm = self.llm.is_available()

        if not self._use_llm:
            logger.info("Ollama服务不可用，将使用默认描述模板")

    def generate_map_description(self, map_type: str, level: int) -> str:
        """
        生成地图描述

        Args:
            map_type: 地图类型
            level: 地图等级

        Returns:
            str: 地图描述
        """
        if self._use_llm:
            prompt = self.templates.generate_map_description(map_type, level)
            fallback = self.DEFAULT_DESCRIPTIONS["map"].get(
                map_type,
                f"此处是一处{map_type}，灵气缭绕，神秘莫测。"
            )
            return self.llm.generate_with_fallback(prompt, fallback)
        else:
            return self.DEFAULT_DESCRIPTIONS["map"].get(
                map_type,
                f"此处是一处{map_type}，灵气缭绕，神秘莫测。"
            )

    def generate_npc_description(self, name: str, occupation: str, personality: str) -> str:
        """
        生成NPC描述

        Args:
            name: NPC姓名
            occupation: NPC职业
            personality: NPC性格

        Returns:
            str: NPC描述
        """
        if self._use_llm:
            prompt = self.templates.generate_npc_description(name, occupation, personality)
            fallback = self.DEFAULT_DESCRIPTIONS["npc"].get(
                occupation,
                f"{name}是一位{occupation}，性格{personality}，气质不凡。"
            )
            return self.llm.generate_with_fallback(prompt, fallback)
        else:
            return self.DEFAULT_DESCRIPTIONS["npc"].get(
                occupation,
                f"{name}是一位{occupation}，性格{personality}，气质不凡。"
            )

    def generate_item_description(self, item_type: str, rarity: str) -> str:
        """
        生成物品描述

        Args:
            item_type: 物品类型
            rarity: 稀有度

        Returns:
            str: 物品描述
        """
        if self._use_llm:
            prompt = self.templates.generate_item_description(item_type, rarity)
            fallback = self.DEFAULT_DESCRIPTIONS["item"].get(
                item_type,
                f"这是一件{rarity}的{item_type}，散发着淡淡的灵光。"
            )
            return self.llm.generate_with_fallback(prompt, fallback)
        else:
            return self.DEFAULT_DESCRIPTIONS["item"].get(
                item_type,
                f"这是一件{rarity}的{item_type}，散发着淡淡的灵光。"
            )

    def generate_monster_description(self, monster_type: str, level: int) -> str:
        """
        生成妖兽描述

        Args:
            monster_type: 妖兽类型
            level: 妖兽等级

        Returns:
            str: 妖兽描述
        """
        if self._use_llm:
            prompt = self.templates.generate_monster_description(monster_type, level)
            fallback = self.DEFAULT_DESCRIPTIONS["monster"].get(
                monster_type,
                f"这是一只等级{level}的{monster_type}，妖气弥漫，凶性毕露。"
            )
            return self.llm.generate_with_fallback(prompt, fallback)
        else:
            return self.DEFAULT_DESCRIPTIONS["monster"].get(
                monster_type,
                f"这是一只等级{level}的{monster_type}，妖气弥漫，凶性毕露。"
            )

    def refresh_availability(self) -> bool:
        """
        刷新Ollama服务可用性状态

        Returns:
            bool: 当前可用性状态
        """
        self._use_llm = self.llm.is_available()
        return self._use_llm


# 全局实例，方便直接导入使用
_default_generator: Optional[DescriptionGenerator] = None


def get_description_generator() -> DescriptionGenerator:
    """
    获取默认的描述生成器实例

    Returns:
        DescriptionGenerator: 描述生成器实例
    """
    global _default_generator
    if _default_generator is None:
        _default_generator = DescriptionGenerator()
    return _default_generator


# 便捷函数，可以直接调用
def generate_map_description(map_type: str, level: int) -> str:
    """生成地图描述"""
    return get_description_generator().generate_map_description(map_type, level)


def generate_npc_description(name: str, occupation: str, personality: str) -> str:
    """生成NPC描述"""
    return get_description_generator().generate_npc_description(name, occupation, personality)


def generate_item_description(item_type: str, rarity: str) -> str:
    """生成物品描述"""
    return get_description_generator().generate_item_description(item_type, rarity)


def generate_monster_description(monster_type: str, level: int) -> str:
    """生成妖兽描述"""
    return get_description_generator().generate_monster_description(monster_type, level)


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试 LocalLLM 和 PromptTemplates")
    print("=" * 50)

    # 测试 LocalLLM
    llm = LocalLLM()
    print(f"\nOllama服务可用: {llm.is_available()}")

    # 测试 PromptTemplates
    templates = PromptTemplates()

    print("\n--- 地图描述提示词 ---")
    print(templates.generate_map_description("山脉", 5))

    print("\n--- NPC描述提示词 ---")
    print(templates.generate_npc_description("李逍遥", "剑修", "孤傲"))

    print("\n--- 物品描述提示词 ---")
    print(templates.generate_item_description("法宝", "传说"))

    print("\n--- 妖兽描述提示词 ---")
    print(templates.generate_monster_description("虎妖", 7))

    # 测试 DescriptionGenerator
    print("\n" + "=" * 50)
    print("测试 DescriptionGenerator")
    print("=" * 50)

    generator = DescriptionGenerator()

    print("\n--- 生成的地图描述 ---")
    print(generator.generate_map_description("山脉", 5))

    print("\n--- 生成的NPC描述 ---")
    print(generator.generate_npc_description("李逍遥", "剑修", "孤傲"))

    print("\n--- 生成的物品描述 ---")
    print(generator.generate_item_description("法宝", "传说"))

    print("\n--- 生成的妖兽描述 ---")
    print(generator.generate_monster_description("虎妖", 7))
