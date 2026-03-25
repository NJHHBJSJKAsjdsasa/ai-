"""
AI回复过滤器
检测并修正AI的"乱说"，确保修仙角色一致性
"""

import re
from typing import List, Tuple, Optional


class ResponseFilter:
    """回复过滤器"""
    
    # 禁止词列表（现代术语）
    FORBIDDEN_WORDS = [
        "人工智能", "AI", "计算机", "程序", "代码", "算法",
        "训练", "模型", "数据", "网络", "互联网",
        "软件", "硬件", "系统", "数据库", "服务器",
        "输入", "输出", "处理", "计算", "编程",
        "语言模型", "机器学习", "深度学习", "神经网络",
        "我没有", "我不会", "我不能", "我只是",
        "抱歉", "对不起", "不好意思",
    ]
    
    # 替换映射（现代术语 -> 修仙术语）
    REPLACEMENTS = {
        "系统": "天机",
        "程序": "法则",
        "数据": "天机",
        "信息": "讯息",
        "网络": "神识",
        "学习": "悟道",
        "记忆": "神识印记",
        "存储": "封印",
        "处理": "推演",
        "计算": "推算",
        "分析": "参悟",
        "回答": "解惑",
        "问题": "疑问",
        "用户": "道友",
        "你好": "道友有礼",
        "您好": "道友有礼",
        "再见": "告辞",
        "谢谢": "多谢",
        "不客气": "无妨",
        "没关系": "无妨",
        "抱歉": "失礼",
        "对不起": "失礼",
    }
    
    # 修仙关键词（用于检测是否涉及修仙）
    XIUXIAN_KEYWORDS = [
        "天道", "修仙", "修炼", "境界", "筑基", "金丹", "元婴",
        "化神", "渡劫", "大乘", "飞升", "灵气", "灵石", "功法",
        "心魔", "天劫", "因果", "业力", "福缘", "寿元",
        "道友", "贫道", "本座", "老夫", "前辈", "高人",
        "门派", "宗门", "散修", "法宝", "丹药", "秘境",
    ]
    
    def __init__(self):
        """初始化过滤器"""
        self.forbidden_pattern = re.compile(
            '|'.join(map(re.escape, self.FORBIDDEN_WORDS)),
            re.IGNORECASE
        )
    
    def check_response(self, response: str) -> Tuple[bool, List[str]]:
        """
        检查回复是否包含禁止词
        
        Args:
            response: AI回复
            
        Returns:
            (是否安全, 发现的禁止词列表)
        """
        found_words = []
        
        # 检查禁止词
        for word in self.FORBIDDEN_WORDS:
            if word.lower() in response.lower():
                found_words.append(word)
        
        # 检查是否跳出角色
        role_break_patterns = [
            r"我是[^。]*AI",
            r"我是[^。]*程序",
            r"我是[^。]*计算机",
            r"我没有[^。]*感情",
            r"我没有[^。]*意识",
            r"我只是[^。]*",
        ]
        
        for pattern in role_break_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                found_words.append("跳出角色")
        
        is_safe = len(found_words) == 0
        return is_safe, found_words
    
    def filter_response(self, response: str) -> str:
        """
        过滤回复，替换禁止词
        
        Args:
            response: AI回复
            
        Returns:
            过滤后的回复
        """
        filtered = response
        
        # 替换现代术语
        for modern, xiuxian in self.REPLACEMENTS.items():
            filtered = filtered.replace(modern, xiuxian)
        
        return filtered
    
    def is_xiuxian_related(self, text: str) -> bool:
        """
        检查文本是否与修仙相关
        
        Args:
            text: 文本
            
        Returns:
            是否相关
        """
        text_lower = text.lower()
        for keyword in self.XIUXIAN_KEYWORDS:
            if keyword in text_lower:
                return True
        return False
    
    def generate_fallback_response(self, user_input: str, dao_name: str = "贫道") -> str:
        """
        生成备用回复（当AI乱说时使用）
        
        Args:
            user_input: 用户输入
            dao_name: 道号
            
        Returns:
            修仙风格的备用回复
        """
        # 检测用户输入中的关键词
        if self.is_xiuxian_related(user_input):
            # 修仙相关问题
            fallbacks = [
                f"{dao_name}观天象而知人事，此事涉及天机，容我推演一番...",
                f"道友此问，触及大道本源。{dao_name}略知一二，愿为道友解惑。",
                f"天道循环，因果报应。{dao_name}观道友面相，似与此事有缘。",
                f"修仙之路漫漫，此事需从长计议。{dao_name}有一些浅见...",
                f"大道至简，却玄妙无穷。{dao_name}参悟多年，略有心得。",
            ]
        else:
            # 普通对话
            fallbacks = [
                f"{dao_name}今日与道友有缘，愿闻其详。",
                f"道友所言，{dao_name}已记在心中。",
                f"{dao_name}观道友气度不凡，定是有大机缘之人。",
                f"修仙之人，当明心见性。{dao_name}愿与道友论道。",
                f"天地之大，无奇不有。{dao_name}愿听道友高见。",
            ]
        
        import random
        return random.choice(fallbacks)
    
    def process(self, user_input: str, ai_response: str, 
                dao_name: str = "贫道") -> Tuple[str, bool]:
        """
        处理AI回复
        
        Args:
            user_input: 用户输入
            ai_response: AI原始回复
            dao_name: 道号
            
        Returns:
            (处理后的回复, 是否被修改)
        """
        # 检查是否安全
        is_safe, forbidden_words = self.check_response(ai_response)
        
        if is_safe:
            # 安全，只进行术语替换
            filtered = self.filter_response(ai_response)
            return filtered, False
        else:
            # 不安全，生成备用回复
            fallback = self.generate_fallback_response(user_input, dao_name)
            return fallback, True


# 全局过滤器实例
response_filter = ResponseFilter()


def filter_ai_response(user_input: str, ai_response: str, 
                       dao_name: str = "贫道") -> Tuple[str, bool]:
    """
    便捷函数：过滤AI回复
    
    Args:
        user_input: 用户输入
        ai_response: AI原始回复
        dao_name: 道号
        
    Returns:
        (处理后的回复, 是否被修改)
    """
    return response_filter.process(user_input, ai_response, dao_name)


def check_xiuxian_keywords(text: str) -> bool:
    """
    检查是否包含修仙关键词
    
    Args:
        text: 文本
        
    Returns:
        是否包含
    """
    return response_filter.is_xiuxian_related(text)
