import re
from typing import Dict, List, Tuple


class Selector:
    """重要性评分系统 - 评估内容是否值得记忆"""

    # 问题关键词
    QUESTION_KEYWORDS = [
        '什么', '怎么', '为什么', '如何', '哪里', '谁', '多少', '几',
        '吗', '呢', '吧', '么', '能否', '是否', '有没有', '可不可以'
    ]

    # 第一人称词汇
    FIRST_PERSON_WORDS = [
        '我', '我的', ' myself', ' me', ' my ', ' mine'
    ]

    # 情感词
    EMOTION_WORDS = {
        'positive': ['喜欢', '爱', '开心', '高兴', '快乐', '幸福', '满意', '期待', '兴奋', '感动', '感谢'],
        'negative': ['讨厌', '恨', '难过', '伤心', '失望', '生气', '愤怒', '焦虑', '担心', '害怕', '烦'],
        'strong': ['非常', '特别', '极其', '超级', '太', '很', '真的', '绝对', '完全']
    }

    # 数字模式
    NUMBER_PATTERNS = [
        r'\d+',  # 纯数字
        r'\d{4}年',  # 年份
        r'\d{1,2}月',  # 月份
        r'\d{1,2}日',  # 日期
        r'\d{1,2}:\d{2}',  # 时间
    ]

    def __init__(self):
        self.min_length = 5
        self.max_length = 500
        self.remember_threshold = 3

    def calculate_importance(self, content: str) -> float:
        """
        计算内容的重要性分数 (0-10)

        评分维度：
        1. 内容长度评分
        2. 问题检测评分
        3. 个人信息检测
        4. 数字/日期检测
        5. 情感强度评分
        """
        if not content or not isinstance(content, str):
            return 0.0

        content = content.strip()
        if not content:
            return 0.0

        score = 5.0  # 基础分

        # 1. 内容长度评分
        length_score = self._calculate_length_score(content)
        score += length_score

        # 2. 问题检测评分
        question_score = self._calculate_question_score(content)
        score += question_score

        # 3. 个人信息检测
        personal_score = self._calculate_personal_score(content)
        score += personal_score

        # 4. 数字/日期检测
        number_score = self._calculate_number_score(content)
        score += number_score

        # 5. 情感强度评分
        emotion_score = self._calculate_emotion_score(content)
        score += emotion_score

        # 确保分数在 0-10 范围内
        return max(0.0, min(10.0, round(score, 1)))

    def _calculate_length_score(self, content: str) -> float:
        """根据内容长度计算分数"""
        length = len(content)

        if length < self.min_length:
            # 太短扣分 (-2 到 -3)
            return -3.0 + (length / self.min_length)
        elif length > self.max_length:
            # 太长扣分 (-1 到 -2)
            excess_ratio = (length - self.max_length) / self.max_length
            return -1.0 - min(1.0, excess_ratio)
        else:
            # 适中加分 (+0 到 +1)
            optimal_length = 50
            if length <= optimal_length:
                return 1.0 * (length / optimal_length)
            else:
                return max(0, 1.0 - (length - optimal_length) / 200)

    def _calculate_question_score(self, content: str) -> float:
        """检测问题并评分"""
        score = 0.0

        # 检查疑问词
        for keyword in self.QUESTION_KEYWORDS:
            if keyword in content:
                score += 1.5
                break

        # 检查问号
        if '？' in content or '?' in content:
            score += 1.0

        return min(2.5, score)

    def _calculate_personal_score(self, content: str) -> float:
        """检测个人信息并评分"""
        score = 0.0

        for word in self.FIRST_PERSON_WORDS:
            if word in content:
                score += 1.0
                break

        # 检测个人信息模式
        personal_patterns = [
            r'我(?:叫|是|来自|住在|喜欢|讨厌|想|要)',
            r'我的(?:名字|家乡|爱好|兴趣|工作|专业|年龄)'
        ]

        for pattern in personal_patterns:
            if re.search(pattern, content):
                score += 0.5

        return min(2.0, score)

    def _calculate_number_score(self, content: str) -> float:
        """检测数字/日期并评分"""
        score = 0.0

        for pattern in self.NUMBER_PATTERNS:
            matches = re.findall(pattern, content)
            score += len(matches) * 0.3

        return min(1.5, score)

    def _calculate_emotion_score(self, content: str) -> float:
        """检测情感强度并评分"""
        score = 0.0

        # 正面情感
        for word in self.EMOTION_WORDS['positive']:
            if word in content:
                score += 0.4

        # 负面情感
        for word in self.EMOTION_WORDS['negative']:
            if word in content:
                score += 0.4

        # 强度词
        for word in self.EMOTION_WORDS['strong']:
            if word in content:
                score += 0.3

        return min(1.5, score)

    def should_remember(self, content: str) -> bool:
        """
        判断是否值得记忆

        规则：重要性 >= 3 才值得记忆
        """
        importance = self.calculate_importance(content)
        return importance >= self.remember_threshold

    def evaluate_importance(self, content: str) -> float:
        """
        评估内容重要性（兼容接口）

        Args:
            content: 要评估的内容

        Returns:
            重要性分数 (0-10)
        """
        return self.calculate_importance(content)

    def is_worth_remembering(self, content: str, importance: float = None) -> bool:
        """
        判断是否值得记忆（兼容接口）

        Args:
            content: 要判断的内容
            importance: 重要性分数（可选，如果不提供则自动计算）

        Returns:
            是否值得记忆
        """
        if importance is None:
            importance = self.calculate_importance(content)
        return importance >= self.remember_threshold

    def get_category(self, content: str) -> str:
        """
        根据内容推断分类

        分类：问题、个人信息、事实、闲聊
        """
        if not content or not isinstance(content, str):
            return 'unknown'

        content = content.strip()

        # 检测是否为问题
        is_question = self._is_question(content)

        # 检测是否为个人信息
        is_personal = self._is_personal_info(content)

        # 检测是否为事实
        is_fact = self._is_fact(content)

        if is_question:
            return 'question'
        elif is_personal:
            return 'personal_info'
        elif is_fact:
            return 'fact'
        else:
            return 'chat'

    def _is_question(self, content: str) -> bool:
        """判断是否为问题"""
        # 检查问号
        if '？' in content or '?' in content:
            return True

        # 检查疑问词
        for keyword in self.QUESTION_KEYWORDS:
            if keyword in content:
                return True

        return False

    def _is_personal_info(self, content: str) -> bool:
        """判断是否为个人信息"""
        # 检查第一人称
        for word in self.FIRST_PERSON_WORDS:
            if word in content:
                return True

        # 检查个人信息模式
        personal_patterns = [
            r'我(?:叫|是|来自|住在|喜欢|讨厌|想|要|觉得|认为)',
            r'我的(?:名字|家乡|爱好|兴趣|工作|专业|年龄|生日|电话)'
        ]

        for pattern in personal_patterns:
            if re.search(pattern, content):
                return True

        return False

    def _is_fact(self, content: str) -> bool:
        """判断是否为事实陈述"""
        # 包含具体数据
        if re.search(r'\d+', content):
            return True

        # 包含日期/时间
        if re.search(r'\d{4}年|\d{1,2}月|\d{1,2}日', content):
            return True

        # 包含专有名词指示词
        fact_indicators = ['是', '有', '在', '位于', '成立于', '创建于', '发明于']
        for indicator in fact_indicators:
            if indicator in content:
                return True

        return False

    def analyze(self, content: str) -> Dict:
        """
        全面分析内容，返回详细评分报告
        """
        importance = self.calculate_importance(content)
        category = self.get_category(content)
        should_remember = self.should_remember(content)

        return {
            'content': content,
            'importance': importance,
            'category': category,
            'should_remember': should_remember,
            'details': {
                'length_score': self._calculate_length_score(content),
                'question_score': self._calculate_question_score(content),
                'personal_score': self._calculate_personal_score(content),
                'number_score': self._calculate_number_score(content),
                'emotion_score': self._calculate_emotion_score(content)
            }
        }


# 便捷函数
def calculate_importance(content: str) -> float:
    """计算内容重要性分数"""
    selector = Selector()
    return selector.calculate_importance(content)


def should_remember(content: str) -> bool:
    """判断内容是否值得记忆"""
    selector = Selector()
    return selector.should_remember(content)


def get_category(content: str) -> str:
    """获取内容分类"""
    selector = Selector()
    return selector.get_category(content)


if __name__ == '__main__':
    # 测试示例
    selector = Selector()

    test_cases = [
        "什么是深度学习？",
        "我叫小明，今年25岁。",
        "今天天气不错。",
        "啊啊啊",
        "我非常喜欢机器学习，因为它能解决很多实际问题。",
        "2024年人工智能发展很快。",
        "你好",
        "如何学习Python编程？我想成为一名数据科学家。"
    ]

    print("=" * 60)
    print("重要性评分系统测试")
    print("=" * 60)

    for content in test_cases:
        result = selector.analyze(content)
        print(f"\n内容: {content}")
        print(f"  重要性: {result['importance']}/10")
        print(f"  分类: {result['category']}")
        print(f"  值得记忆: {'是' if result['should_remember'] else '否'}")
        print(f"  详细评分: {result['details']}")
