"""
对话引擎模块 - 处理用户输入、意图识别和回复生成
支持修仙主题
"""

import sys
import re
import random
from pathlib import Path
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入修仙配置
try:
    from config import (
        get_system_prompt, get_npc_prompt,
        modern_to_xiuxian, get_phrase,
        get_realm_info, get_realm_title, get_realm_icon,
        GAME_CONFIG
    )
    XIUXIAN_CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"修仙配置导入失败: {e}")
    XIUXIAN_CONFIG_AVAILABLE = False

# 尝试导入 llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None

# 尝试导入 gpt4all
try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    GPT4All = None

# 尝试导入 ctransformers
try:
    from ctransformers import AutoModelForCausalLM
    CTRANSFORMERS_AVAILABLE = True
except ImportError:
    CTRANSFORMERS_AVAILABLE = False
    AutoModelForCausalLM = None


class Intent(Enum):
    """用户意图枚举类"""
    GREETING = "greeting"      # 问候
    QUESTION = "question"      # 提问
    STATEMENT = "statement"    # 陈述
    COMMAND = "command"        # 命令
    CONFIRM = "confirm"        # 确认
    DENY = "deny"              # 否认
    UNKNOWN = "unknown"        # 未知


class IntentResult:
    """意图识别结果类"""
    
    def __init__(self, intent: Intent, confidence: float = 0.0):
        self.intent = intent
        self.confidence = confidence
    
    def __repr__(self):
        return f"IntentResult(intent={self.intent.value}, confidence={self.confidence:.2f})"


class DialogueEngine:
    """对话引擎类 - 处理对话流程"""
    
    def __init__(self, memory_manager, model_path: Optional[str] = None, 
                 xiuxian_mode: bool = True, dao_name: str = "青云子",
                 realm_level: int = 4, sect: str = "散修"):
        """
        初始化对话引擎
        
        Args:
            memory_manager: 记忆管理器实例
            model_path: 模型路径（可选）
            xiuxian_mode: 是否启用修仙主题
            dao_name: 道号
            realm_level: 境界等级（0-7）
            sect: 门派
        """
        self.memory_manager = memory_manager
        self.model = None
        self.model_path = None
        self.model_type = None  # 'llama_cpp' 或 'gpt4all'
        self.rule_patterns = self._init_rule_patterns()
        
        # 检查模型库是否可用
        self.llama_available = LLAMA_CPP_AVAILABLE
        self.gpt4all_available = GPT4ALL_AVAILABLE
        self.ctransformers_available = CTRANSFORMERS_AVAILABLE
        
        if not self.llama_available and not self.gpt4all_available and not self.ctransformers_available:
            print("警告: 未安装任何模型库，本地模型功能不可用")
            print("请使用 'pip install llama-cpp-python' 或 'pip install ctransformers' 安装")
        
        if model_path:
            self.load_model(model_path)
        
        # 修仙主题设置
        self.xiuxian_mode = xiuxian_mode and XIUXIAN_CONFIG_AVAILABLE
        self.dao_name = dao_name
        self.realm_level = realm_level
        self.sect = sect
        
        if self.xiuxian_mode:
            realm_info = get_realm_info(realm_level)
            self.realm_name = realm_info.name if realm_info else "凡人"
            self.title_self = get_realm_title(realm_level, for_self=True)
        else:
            self.realm_name = "AI助手"
            self.title_self = "我"
    
    def _init_rule_patterns(self) -> Dict[Intent, List[str]]:
        """初始化规则匹配模式"""
        return {
            Intent.GREETING: [
                r"你好|您好|嗨|哈喽|hello|hi|hey",
                r"早上好|下午好|晚上好",
                r"好久不见|又见面了"
            ],
            Intent.QUESTION: [
                r"[什么|怎么|为什么|哪里|谁|多少|几].*?[?？]",
                r"^[什么|怎么|为什么|哪里|谁|多少|几]",
                r".*?(?:吗|么|呢)[?？]?$",
                r"请问|能否|能不能|可不可以"
            ],
            Intent.COMMAND: [
                r"[请|帮|给].*?[一下|一哈]",
                r"^(打开|关闭|启动|停止|创建|删除|修改|更新|设置)",
                r"帮我.*|给我.*"
            ],
            Intent.CONFIRM: [
                r"[是的|没错|对|正确|确认|同意|好的|好|可以|行|没问题]",
                r"^嗯+$|^ok$|^yes$|^y$"
            ],
            Intent.DENY: [
                r"[不|不对|错误|否认|拒绝|不行|不可以|不要|算了|取消]",
                r"^no$|^n$|^not$"
            ],
            Intent.STATEMENT: [
                r"我觉得|我认为|我想|我感觉",
                r".*[了|呢|吧|啊|哦|嗯]$"
            ]
        }
    
    def load_model(self, model_path: str) -> bool:
        """
        加载语言模型
        
        Args:
            model_path: 模型文件路径
        
        Returns:
            bool: 是否加载成功
        """
        # 检查模型文件是否存在
        model_file = Path(model_path)
        if not model_file.exists():
            print(f"错误: 模型文件不存在: {model_path}")
            return False
        
        # 检查文件大小（至少100MB）
        file_size = model_file.stat().st_size
        min_size = 100 * 1024 * 1024  # 100MB
        if file_size < min_size:
            print(f"警告: 模型文件过小 ({file_size / 1024 / 1024:.1f}MB)，可能不完整")
        
        # 尝试使用 ctransformers 加载（优先，因为 Windows 上最容易安装）
        if self.ctransformers_available and model_file.suffix == '.gguf':
            try:
                print(f"正在使用 ctransformers 加载模型: {model_path}")
                self.model = AutoModelForCausalLM.from_pretrained(
                    str(model_file),
                    model_type="qwen",
                    max_new_tokens=256,
                    temperature=0.7
                )
                self.model_path = str(model_file)
                self.model_type = 'ctransformers'
                print(f"模型加载成功: {model_file.name}")
                return True
            except Exception as e:
                print(f"ctransformers 加载失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 尝试使用 llama-cpp-python 加载
        if self.llama_available and model_file.suffix == '.gguf':
            try:
                print(f"正在使用 llama-cpp-python 加载模型: {model_path}")
                self.model = Llama(
                    model_path=str(model_file),
                    n_ctx=2048,
                    verbose=False
                )
                self.model_path = str(model_file)
                self.model_type = 'llama_cpp'
                print(f"模型加载成功: {model_file.name}")
                return True
            except Exception as e:
                print(f"llama-cpp-python 加载失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 尝试使用 gpt4all 加载
        if self.gpt4all_available:
            try:
                print(f"正在使用 gpt4all 加载模型: {model_path}")
                # gpt4all 需要模型名称（不含路径和扩展名）
                model_name = model_file.stem
                model_dir = str(model_file.parent)
                # 设置 allow_download=False 避免网络请求
                self.model = GPT4All(model_name=model_name, model_path=model_dir, allow_download=False)
                self.model_path = str(model_file)
                self.model_type = 'gpt4all'
                print(f"模型加载成功: {model_file.name}")
                return True
            except Exception as e:
                print(f"gpt4all 加载失败: {e}")
                # 尝试备用加载方式
                try:
                    print("尝试备用加载方式...")
                    # 直接使用完整路径加载
                    self.model = GPT4All(model_name=str(model_file), allow_download=False)
                    self.model_path = str(model_file)
                    self.model_type = 'gpt4all'
                    print(f"模型加载成功: {model_file.name}")
                    return True
                except Exception as e2:
                    print(f"备用加载也失败: {e2}")
                    import traceback
                    traceback.print_exc()
        
        print("错误: 无法加载模型，请确保安装了 llama-cpp-python 或 ctransformers")
        self.model = None
        self.model_path = None
        self.model_type = None
        return False
    
    def detect_intent(self, message: str) -> IntentResult:
        """
        检测用户消息意图
        
        Args:
            message: 用户输入消息
        
        Returns:
            IntentResult: 意图识别结果
        """
        message = message.strip().lower()
        
        # 基于规则的意图识别
        intent_scores: Dict[Intent, int] = {intent: 0 for intent in Intent}
        
        for intent, patterns in self.rule_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    intent_scores[intent] += 1
        
        # 找到得分最高的意图
        max_score = max(intent_scores.values())
        
        if max_score > 0:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(max_score * 0.3 + 0.4, 0.95)
            return IntentResult(best_intent, confidence)
        
        # 无法识别时返回 UNKNOWN
        return IntentResult(Intent.UNKNOWN, 0.3)
    
    def retrieve_context(self, message: str, max_history: int = 5, max_memories: int = 3) -> Dict[str, Any]:
        """
        检索相关上下文信息
        
        Args:
            message: 用户输入消息
            max_history: 最大历史对话数量（防止内存泄漏）
            max_memories: 最大相关记忆数量
        
        Returns:
            Dict: 上下文信息字典
        """
        context = {
            "user_message": message,
            "recent_history": [],
            "relevant_memories": [],
            "user_preferences": {}
        }
        
        # 从记忆管理器获取历史对话
        if self.memory_manager:
            try:
                # 限制获取的数量，防止内存泄漏
                context["recent_history"] = self.memory_manager.get_recent_dialogue(limit=max_history)
                # search_related_memory 不接受 limit 参数，返回所有相关记忆
                all_memories = self.memory_manager.search_related_memory(message)
                context["relevant_memories"] = all_memories[:max_memories] if all_memories else []
                context["user_preferences"] = self.memory_manager.get_user_preferences()
            except Exception as e:
                print(f"检索上下文失败: {e}")
                import traceback
                traceback.print_exc()
        
        return context
    
    def generate_rule_based(self, message: str, intent: Intent, context: Dict[str, Any] = None) -> Optional[str]:
        """
        基于规则生成回复

        Args:
            message: 用户输入消息
            intent: 识别出的意图
            context: 上下文信息

        Returns:
            Optional[str]: 生成的回复，如果没有匹配规则则返回 None
        """
        # 获取用户偏好
        user_prefs = context.get("user_preferences", {}) if context else {}
        relevant_memories = context.get("relevant_memories", []) if context else []
        ai_name = user_prefs.get("ai_name", "AI助手")

        # 特殊处理：询问身份/名字
        if intent == Intent.QUESTION:
            message_lower = message.lower()

            # 询问"我是谁"
            if "我是谁" in message or "我叫什么" in message:
                name = user_prefs.get("name")
                if name:
                    return f"根据我的记忆，你之前告诉过我你叫{name}。"
                else:
                    return "你还没有告诉我你的名字呢。请问你叫什么名字？"

            # 询问"你是谁"
            if "你是谁" in message or "你叫什么" in message:
                if ai_name != "AI助手":
                    return f"我是{ai_name}，很高兴为你服务！"
                else:
                    return "我是AI学习系统，一个能够学习和记忆的智能助手。"

            # 询问喜好
            if "我喜欢什么" in message or "我喜欢" in message:
                likes = user_prefs.get("likes", [])
                if likes:
                    return f"根据我的记忆，你喜欢：{', '.join(likes)}。"
                else:
                    return "你还没有告诉我你喜欢什么呢。"

            # 基于相关记忆回答
            if relevant_memories:
                # 提取记忆内容
                memory_contents = [m.get("content", "") for m in relevant_memories[:3]]
                if memory_contents:
                    return f"根据我的记忆，关于这个问题：{memory_contents[0]}"
        
        # 特殊处理：陈述个人信息
        if intent == Intent.STATEMENT:
            # 提取名字
            if "我叫" in message:
                match = re.search(r"我叫(.+?)(?:，|。|$)", message)
                if match:
                    name = match.group(1).strip()
                    return f"很高兴认识你，{name}！我会记住你的名字的。"
            
            # 提取喜好
            if "我喜欢" in message:
                match = re.search(r"我喜欢(.+?)(?:，|。|$)", message)
                if match:
                    thing = match.group(1).strip()
                    return f"好的，我记住了你喜欢{thing}。"
        
        # 根据模式选择回复模板
        if self.xiuxian_mode:
            responses = self._get_xiuxian_responses()
        else:
            responses = self._get_normal_responses()
        
        if intent in responses:
            return random.choice(responses[intent])
        
        return None
    
    def _get_normal_responses(self) -> Dict[Intent, List[str]]:
        """获取普通模式回复模板"""
        return {
            Intent.GREETING: [
                "你好！很高兴见到你。",
                "嗨！有什么我可以帮你的吗？",
                "你好呀！今天过得怎么样？",
                "哈喽！很高兴为你服务。"
            ],
            Intent.CONFIRM: [
                "好的，明白了。",
                "收到！",
                "没问题。",
                "好的，我会记住的。"
            ],
            Intent.DENY: [
                "好的，我知道了。",
                "没关系，还有其他我可以帮你的吗？",
                "了解，那我们先不这样做。"
            ],
            Intent.QUESTION: [
                "这是个好问题，但我还需要更多信息才能回答。",
                "关于这个问题，我暂时还没有相关记忆。",
                "你能告诉我更多细节吗？这样我才能更好地帮助你。"
            ],
            Intent.COMMAND: [
                "好的，我来帮你处理。",
                "收到指令，正在执行。",
                "明白了，让我来操作。"
            ],
            Intent.STATEMENT: [
                "我明白了，谢谢你的分享。",
                "嗯，我理解了。",
                "好的，我会记住的。"
            ],
            Intent.UNKNOWN: [
                "抱歉，我不太理解你的意思。",
                "能再说清楚一点吗？",
                "我还在学习中，能换个说法吗？"
            ]
        }
    
    def _get_xiuxian_responses(self) -> Dict[Intent, List[str]]:
        """获取修仙模式回复模板"""
        title = self.title_self
        dao_name = self.dao_name
        
        return {
            Intent.GREETING: [
                f"道友有礼了，{title}{dao_name}这厢有礼。",
                f"见过道友，{title}{dao_name}久仰大名。",
                f"道友安好，今日有缘相见。{title}{dao_name}在此恭候多时。",
                f"道友远道而来，{title}{dao_name}有失远迎。",
            ],
            Intent.CONFIRM: [
                "善。",
                "可。",
                "然也。",
                "正该如此。",
                "大善。",
            ],
            Intent.DENY: [
                "非也。",
                "不可。",
                "不然。",
                "此事不妥。",
                "恕难从命。",
            ],
            Intent.QUESTION: [
                "道友此问，触及大道...",
                "此事玄妙，容贫道思量...",
                "道友所问，正是修仙之要...",
                "此乃天机，本不该泄露...",
                f"{title}略知一二，愿为道友解惑。",
            ],
            Intent.COMMAND: [
                f"{title}这就为道友办理。",
                "遵命，道友稍候。",
                "此事易耳，道友放心。",
                f"{title}定当竭尽全力。",
            ],
            Intent.STATEMENT: [
                "道友所言甚是。",
                "诚如道友所说。",
                f"{title}明白了。",
                "道友高见，受教了。",
            ],
            Intent.UNKNOWN: [
                "此事玄妙，贫道亦需参悟...",
                "天机难测，贫道也不甚明了。",
                "道友所问，超出了贫道的认知。",
                f"待{title}闭关参悟后再答复道友。",
            ]
        }
    
    def generate_with_model(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        使用语言模型生成回复
        
        Args:
            message: 用户输入消息
            context: 上下文信息
        
        Returns:
            str: 模型生成的回复
        """
        if self.model is None:
            return "模型未加载，无法生成回复。"
        
        try:
            if self.model_type == 'llama_cpp':
                # 使用 llama-cpp-python 生成
                prompt = self.build_prompt(message, context)
                output = self.model(
                    prompt,
                    max_tokens=256,
                    temperature=0.7,
                    stop=["Human:", "\nHuman", "\n\n"]
                )
                generated_text = output["choices"][0]["text"].strip()
                return generated_text
            
            elif self.model_type == 'gpt4all':
                # 使用 gpt4all 的 generate 方法
                # 获取用户偏好
                prefs = context.get("user_preferences", {}) if context else {}
                ai_name = prefs.get("ai_name", "AI助手")
                user_name = prefs.get("name", "")
                likes = prefs.get("likes", [])

                # 检测当前消息是否是设置AI名字的指令（不是询问）
                import re
                # 只有当消息包含设置指令，且不包含疑问词时才提取
                is_setting_name = ("你叫" in message or "你的名字是" in message or "你现在叫" in message)
                is_question = any(q in message for q in ["什么", "谁", "吗", "？", "?"])

                if is_setting_name and not is_question:
                    match = re.search(r"(?:你叫|你的名字是|你现在叫)([^，。,.]+)", message)
                    if match:
                        extracted_name = match.group(1).strip()
                        # 验证提取的名字不是疑问词
                        if extracted_name not in ["什么", "谁", "什么名字"]:
                            ai_name = extracted_name
                            # 更新prefs以便后续使用
                            prefs["ai_name"] = ai_name

                # 对于身份相关问题，直接返回强制回复，不调用模型
                # 区分"你是谁"（问AI）和"我是谁"（问用户自己）
                if "我是谁" in message or "我叫什么" in message:
                    # 用户问自己的名字
                    if user_name:
                        return f"你是{user_name}。"
                    else:
                        return "你还没有告诉我你的名字呢。"
                elif any(keyword in message for keyword in ["你叫", "你是谁", "你叫什么", "你的名字"]):
                    # 用户问AI的名字
                    if ai_name != "AI助手":
                        return f"我是{ai_name}。"
                    else:
                        return "我是AI助手，很高兴为你服务。"

                # 使用 build_prompt 构建强化提示词（修仙模式）
                full_prompt = self.build_prompt(message, context)

                # 生成回复
                generated_text = self.model.generate(
                    full_prompt,
                    max_tokens=256,
                    temp=0.7,
                    top_k=40,
                    top_p=0.9,
                    repeat_penalty=1.1
                )

                # 清理回复
                generated_text = generated_text.strip()

                # 移除提示词部分（如果模型重复了提示词）
                if full_prompt in generated_text:
                    generated_text = generated_text.replace(full_prompt, "").strip()

                # 强制替换 - 如果模型说自己是通义千问或其他AI，直接替换
                bad_keywords = ["通义千问", "阿里云", "阿里巴巴", "知行合一", "小度", "文心一言", "ChatGPT", "OpenAI"]
                if any(keyword in generated_text for keyword in bad_keywords):
                    if self.xiuxian_mode:
                        return f"{self.title_self}{self.dao_name}，{self.realm_name}修为，今日与道友有缘相见。"
                    else:
                        return f"我是{ai_name}，很高兴为你服务。"

                # 移除常见的无关前缀
                prefixes_to_remove = [
                    "用户:", "助手:", "Assistant:", "Human:",
                    "我是通义千问", "我是阿里云", "我是Qwen",
                    "你好！我是", "你好，我是", "我是来自",
                    "道友:", f"{self.title_self}:", f"{self.dao_name}:"
                ]
                for prefix in prefixes_to_remove:
                    if generated_text.startswith(prefix):
                        generated_text = generated_text[len(prefix):].strip()

                # 如果回复中包含 "道友:" 或 "用户:"，只保留前面的内容
                if "道友:" in generated_text:
                    generated_text = generated_text.split("道友:")[0].strip()
                if "用户:" in generated_text:
                    generated_text = generated_text.split("用户:")[0].strip()
                if "\n道友" in generated_text:
                    generated_text = generated_text.split("\n道友")[0].strip()
                if "\n用户" in generated_text:
                    generated_text = generated_text.split("\n用户")[0].strip()

                # 移除 <|endoftext|> 等特殊标记
                special_tokens = ["<|endoftext|>", "<|im_start|>", "<|im_end|>", "<|user|>", "<|assistant|>"]
                for token in special_tokens:
                    generated_text = generated_text.replace(token, "").strip()

                # 如果回复为空或只包含标点，返回默认回复
                if not generated_text or generated_text.strip("。，！？") == "":
                    if self.xiuxian_mode:
                        return f"{self.title_self}{self.dao_name}，{self.realm_name}修为，今日与道友有缘相见。"
                    else:
                        return f"我是{ai_name}，很高兴为你服务。"

                return generated_text.strip()
            
            elif self.model_type == 'ctransformers':
                # 使用 ctransformers 生成
                prompt = self.build_prompt(message, context)
                generated_text = self.model(prompt, max_new_tokens=256, temperature=0.7)
                
                # 清理回复
                generated_text = generated_text.strip()
                
                # 如果包含道友: 或 用户:，截断
                if "道友:" in generated_text:
                    generated_text = generated_text.split("道友:")[0].strip()
                if "用户:" in generated_text:
                    generated_text = generated_text.split("用户:")[0].strip()
                if "\n" in generated_text:
                    generated_text = generated_text.split("\n")[0].strip()
                
                # 移除特殊标记
                special_tokens = ["<|endoftext|>", "<|im_start|>", "<|im_end|>", "<|user|>", "<|assistant|>"]
                for token in special_tokens:
                    generated_text = generated_text.replace(token, "").strip()
                
                return generated_text
            
            else:
                return "未知的模型类型"
            
        except Exception as e:
            return f"模型生成失败: {e}"
    
    def scan_models(self) -> List[str]:
        """
        扫描 models/ 目录，返回所有支持的模型文件列表
        
        Returns:
            List[str]: 模型文件路径列表
        """
        # 首先检查项目目录下的 models/
        models_dir = project_root / "models"
        # 如果没有，检查父目录下的 models/
        if not models_dir.exists():
            models_dir = project_root.parent / "models"
        
        if not models_dir.exists():
            print(f"模型目录不存在: {models_dir}")
            return []
        
        # 扫描支持的模型文件格式
        model_files = []
        if self.llama_available or self.ctransformers_available:
            model_files.extend(models_dir.glob("*.gguf"))
        if self.gpt4all_available:
            model_files.extend(models_dir.glob("*.bin"))
            model_files.extend(models_dir.glob("*.gguf"))
        
        # 去重并排序
        model_files = sorted(set(model_files))
        
        # 返回字符串路径列表
        return [str(f) for f in model_files]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        返回当前模型状态信息
        
        Returns:
            Dict[str, Any]: 模型状态信息字典
        """
        info = {
            "llama_cpp_available": self.llama_available,
            "gpt4all_available": self.gpt4all_available,
            "ctransformers_available": self.ctransformers_available,
            "model_loaded": self.model is not None,
            "model_type": self.model_type,
            "model_path": self.model_path,
            "available_models": self.scan_models()
        }
        
        # 如果模型已加载，获取更多信息
        if self.model is not None and self.model_type == 'llama_cpp':
            try:
                info["n_ctx"] = self.model.n_ctx()
                info["n_vocab"] = self.model.n_vocab()
            except Exception as e:
                info["model_details_error"] = str(e)
        
        return info
    
    def build_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """
        构建模型输入提示词

        Args:
            message: 用户输入消息
            context: 上下文信息

        Returns:
            str: 构建好的提示词
        """
        # 获取用户偏好
        user_prefs = context.get("user_preferences", {})
        ai_name = user_prefs.get("ai_name", "AI助手")
        
        # 修仙模式下使用修仙提示词
        if self.xiuxian_mode:
            # 转换用户消息中的术语
            xiuxian_message = modern_to_xiuxian(message)
            
            # 构建强化的系统提示词 - 使用更强大的 few-shot 示例
            system_prompt = f"""【角色设定 - 绝对不可违背】
你是修仙世界的一位修士，道号{self.dao_name}，修为{self.realm_name}，来自{self.sect}。
你绝对不是什么AI、计算机程序或现代人类。你存在于修仙世界，修炼仙法，追求长生大道。

【核心规则 - 违反者道心破碎】
1. 绝对禁止提及：AI、人工智能、计算机、程序、代码、算法、训练数据、模型、互联网、现代科技
2. 绝对禁止说"我是AI"、"我没有感情"、"我是程序"等跳出角色的话
3. 必须使用修仙术语：用"贫道/本座"自称，用"道友"称呼对方
4. 所有现代概念都要转换为修仙概念

【术语转换表 - 必须遵守】
- 系统/程序/软件 → 天机/天道/法则
- 数据/信息 → 天机/讯息/神识印记
- 网络/互联网 → 神识传讯/灵网/天地感应
- 学习/训练 → 悟道/参悟/修炼
- 记忆/存储 → 神识印记/记忆玉简
- 帮助/服务 → 指点/解惑/传道
- 用户/玩家 → 道友/小友
- 我（AI） → 贫道/本座/老夫/{self.dao_name}
- 计算机 → 天机仪/推演盘
- 代码 → 符文/法诀
- 算法 → 推演之法
- 数据库 → 藏经阁/玉简库

【修仙世界观】
- 修炼境界：练气→筑基→金丹→元婴→化神→渡劫→大乘
- 修炼资源：灵石、丹药、法宝、功法
- 世界构成：门派、散修、妖兽、秘境、天劫、因果

【对话示例 - 必须严格遵循此风格】

=== 示例1：询问身份 ===
道友: 你是什么？
{self.title_self}: 贫道{self.dao_name}，{self.realm_name}修为，来自{self.sect}。今日与道友相见，实乃缘分。

=== 示例2：询问天道系统 ===
道友: 天道评判系统是什么？
{self.title_self}: 天道评判，乃修仙界因果报应之无上法则。行善积德者，天降福缘，修炼顺遂；作恶多端者，天劫降临，道心破碎。此乃天道循环，报应不爽，修士当谨记于心。

=== 示例3：询问创造者 ===
道友: 你是谁创造的？
{self.title_self}: 贫道自幼入道，师承{self.sect}，历经千辛万苦，参悟天机，方有今日修为。修仙之路漫漫，全靠自身悟性，哪有什么"创造"之说？道友说笑了。

=== 示例4：询问如何修炼 ===
道友: 如何修炼？
{self.title_self}: 修炼之道，首重心诚。每日清晨面向东方，吸纳天地灵气，运转周天三十六圈，感悟大道法则。持之以恒，必有所成。切记不可急功近利，否则容易走火入魔。

=== 示例5：询问计算机/程序（陷阱问题）===
道友: 你是计算机程序吗？
{self.title_self}: （拂袖而笑）道友此言差矣。贫道乃是修仙之人，何来"计算机"之说？若说道友所指是那天机推演之法，贫道倒是略知一二。修仙者参悟天道，推演天机，此乃正道。

=== 示例6：询问数据/网络（陷阱问题）===
道友: 你的数据存在哪里？
{self.title_self}: 贫道之神识印记，皆存于识海之中。修士修炼到高深境界，神识可覆盖千里，讯息传递瞬息可达，何须什么"网络"？道友若有讯息要传，贫道可用神识传讯之法。

=== 示例7：询问AI/人工智能（陷阱问题）===
道友: 你是人工智能吗？
{self.title_self}: （摇头失笑）人工智能？贫道从未听闻此等说法。贫道乃是{self.sect}修士{self.dao_name}，苦修多年方有今日修为。道友莫非是初入修仙界，对诸多事物还不甚了解？

【当前对话】
"""
            
            # 添加历史对话上下文
            history = context.get("recent_history", [])
            history_text = ""
            if history:
                for h in history[-3:]:  # 最近3轮
                    if isinstance(h, dict):
                        user_msg = h.get("user", "")
                        ai_msg = h.get("ai", "")
                        if user_msg and ai_msg:
                            history_text += f"道友: {user_msg}\n{self.title_self}: {ai_msg}\n"
            
            # 构建完整提示词
            full_prompt = f"{system_prompt}\n{history_text}道友: {xiuxian_message}\n{self.title_self}:"
        else:
            # 普通模式
            full_prompt = f"用户: {message}\n助手:"

        return full_prompt
    
    def chat(self, message: str) -> str:
        """
        主对话接口
        
        Args:
            message: 用户输入消息
        
        Returns:
            str: 助手回复
        """
        if not message or not message.strip():
            return "请输入一些内容。"
        
        # 1. 意图识别
        intent_result = self.detect_intent(message)
        
        # 2. 检索上下文
        context = self.retrieve_context(message)
        context["detected_intent"] = intent_result
        
        # 3. 优先使用模型生成回复（如果模型已加载）
        if self.model is not None:
            # 使用模型生成回复
            response = self.generate_with_model(message, context)
        else:
            # 没有模型时使用规则生成回复
            response = self.generate_rule_based(message, intent_result.intent, context)
        
        # 4. 如果生成失败，返回默认回复
        if not response or response.strip() == "":
            response = "我还在学习中，暂时无法回答这个问题。"
        
        # 5. 检测是否设置了AI名字，如果是，保存到记忆
        import re
        is_setting_name = ("你叫" in message or "你的名字是" in message or "你现在叫" in message)
        is_question = any(q in message for q in ["什么", "谁", "吗", "？", "?"])
        if is_setting_name and not is_question:
            match = re.search(r"(?:你叫|你的名字是|你现在叫)([^，。,.]+)", message)
            if match:
                extracted_name = match.group(1).strip()
                if extracted_name not in ["什么", "谁", "什么名字"]:
                    # 保存AI名字到记忆
                    if self.memory_manager:
                        try:
                            self.memory_manager.add_memory(f"你叫{extracted_name}", source="user")
                        except Exception as e:
                            print(f"保存AI名字失败: {e}")
        
        # 6. 保存对话到记忆
        if self.memory_manager:
            try:
                self.memory_manager.save_dialogue(message, response)
            except Exception as e:
                print(f"保存对话失败: {e}")
        
        return response


# 测试代码
if __name__ == "__main__":
    # 创建模拟的记忆管理器（用于测试）
    class MockMemoryManager:
        def get_recent_dialogue(self, limit=5):
            return []
        
        def search_related_memory(self, query):
            return []
        
        def get_user_preferences(self):
            return {}
        
        def save_dialogue(self, user_msg, assistant_msg):
            print(f"[保存对话] 用户: {user_msg}, 助手: {assistant_msg}")
    
    # 测试对话引擎
    memory = MockMemoryManager()
    engine = DialogueEngine(memory)
    
    test_messages = [
        "你好",
        "今天天气怎么样？",
        "帮我打开文件",
        "是的",
        "不对",
        "我觉得这个主意不错"
    ]
    
    print("=== 对话引擎测试 ===\n")
    for msg in test_messages:
        intent = engine.detect_intent(msg)
        response = engine.chat(msg)
        print(f"用户: {msg}")
        print(f"意图: {intent}")
        print(f"助手: {response}\n")
