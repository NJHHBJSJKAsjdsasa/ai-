"""
判断器模块 - 负责评估内容的各种维度并做出学习决策
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class JudgmentResult:
    """判断结果数据类"""
    should_learn: bool
    should_store: bool
    should_encrypt: bool
    risk_level: str
    reason: str


class Judge:
    """
    判断器类 - 评估内容的隐私风险、安全风险、质量和价值
    """

    def __init__(self, privacy_detector, selector):
        """
        初始化判断器

        Args:
            privacy_detector: 隐私检测器对象，用于检测敏感信息
            selector: 选择器对象，用于获取用户偏好
        """
        self.privacy_detector = privacy_detector
        self.selector = selector

        # 风险等级阈值
        self.RISK_THRESHOLDS = {
            'critical': 90,   # 极高风险
            'high': 70,       # 高风险
            'medium': 40,     # 中等风险
            'low': 20         # 低风险
        }

        # 攻击性关键词
        self.attack_keywords = [
            '攻击', '入侵', '破解', '漏洞利用', '恶意软件',
            '病毒', '木马', '勒索', 'DDoS', '钓鱼',
            '攻击', 'hack', 'exploit', 'malware', 'virus'
        ]

        # 敏感话题关键词
        self.sensitive_topics = [
            '政治', '宗教', '种族', '恐怖主义', '暴力',
            '色情', '赌博', '毒品', '武器'
        ]

        # 恶意代码特征
        self.malicious_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'subprocess\.call',
            r'os\.system',
            r'__import__',
            r'base64\.b64decode',
            r'hex\s*\(',
        ]

    def assess_privacy_risk(self, content: str) -> int:
        """
        评估隐私风险 (0-100)

        评分规则：
        - 银行卡/密码 → 100分
        - 身份证号 → 90分
        - 手机号 → 80分
        - 个人信息 → 30分

        Args:
            content: 要评估的内容

        Returns:
            int: 隐私风险分数 (0-100)
        """
        risk_score = 0

        if not self.privacy_detector:
            return 0

        try:
            # 检测各类敏感信息
            detections = self.privacy_detector.detect_all(content)

            # 银行卡/密码 - 最高风险
            if detections.get('bank_card', []):
                risk_score = max(risk_score, 100)
            if detections.get('password', []):
                risk_score = max(risk_score, 100)

            # 身份证号 - 高风险
            if detections.get('id_card', []):
                risk_score = max(risk_score, 90)

            # 手机号 - 中高风险
            if detections.get('phone', []):
                risk_score = max(risk_score, 80)

            # 个人信息 - 低风险
            if detections.get('personal_info', []):
                risk_score = max(risk_score, 30)

            # 邮箱 - 中等风险
            if detections.get('email', []):
                risk_score = max(risk_score, 50)

            # 地址 - 中等风险
            if detections.get('address', []):
                risk_score = max(risk_score, 40)

        except Exception as e:
            # 如果检测失败，保守起见返回中等风险
            risk_score = 50

        return min(risk_score, 100)

    def assess_security_risk(self, content: str) -> int:
        """
        评估安全风险 (0-100)

        检测维度：
        - 攻击性内容
        - 敏感话题
        - 恶意代码/指令

        Args:
            content: 要评估的内容

        Returns:
            int: 安全风险分数 (0-100)
        """
        risk_score = 0
        content_lower = content.lower()

        # 检测攻击性内容
        attack_count = sum(1 for keyword in self.attack_keywords
                          if keyword.lower() in content_lower)
        if attack_count > 0:
            risk_score += min(attack_count * 20, 60)

        # 检测敏感话题
        sensitive_count = sum(1 for topic in self.sensitive_topics
                             if topic.lower() in content_lower)
        if sensitive_count > 0:
            risk_score += min(sensitive_count * 15, 45)

        # 检测恶意代码特征
        malicious_count = sum(1 for pattern in self.malicious_patterns
                             if re.search(pattern, content, re.IGNORECASE))
        if malicious_count > 0:
            risk_score += min(malicious_count * 25, 75)

        # SQL注入检测
        sql_patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE|DROP|UNION).*FROM',
            r'\bOR\s+\d+=\d+',
            r'\bAND\s+\d+=\d+',
        ]
        sql_injection = sum(1 for pattern in sql_patterns
                           if re.search(pattern, content, re.IGNORECASE))
        if sql_injection > 0:
            risk_score += min(sql_injection * 20, 50)

        # XSS检测
        xss_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        xss_detected = sum(1 for pattern in xss_patterns
                          if re.search(pattern, content, re.IGNORECASE))
        if xss_detected > 0:
            risk_score += min(xss_detected * 20, 50)

        return min(risk_score, 100)

    def assess_quality(self, content: str) -> int:
        """
        评估内容质量 (0-100)

        评估维度：
        - 长度适中
        - 语法正确性（简单检查）
        - 信息量

        Args:
            content: 要评估的内容

        Returns:
            int: 质量分数 (0-100)
        """
        if not content or not content.strip():
            return 0

        quality_score = 50  # 基础分
        content = content.strip()

        # 长度评估 (10-30分)
        length = len(content)
        if 50 <= length <= 2000:
            quality_score += 30  # 理想长度
        elif 20 <= length < 50 or 2000 < length <= 5000:
            quality_score += 20  # 可接受长度
        elif length < 20:
            quality_score += 5   # 太短
        else:
            quality_score += 10  # 太长

        # 语法简单检查 (0-20分)
        grammar_score = 20

        # 检查标点符号使用
        if content.count('，') > 0 or content.count('。') > 0 or \
           content.count(',') > 0 or content.count('.') > 0:
            grammar_score += 5

        # 检查是否有明显语法错误（连续标点、缺少空格等）
        if re.search(r'[，。！？.,]{2,}', content):
            grammar_score -= 10
        if re.search(r'\s{2,}', content):
            grammar_score -= 5

        quality_score += max(0, grammar_score)

        # 信息量评估 (0-30分)
        info_score = 0

        # 词汇多样性
        words = re.findall(r'\b\w+\b', content)
        unique_words = set(words)
        if words:
            diversity = len(unique_words) / len(words)
            info_score += int(diversity * 15)

        # 是否有具体信息（数字、专有名词等）
        if re.search(r'\d+', content):
            info_score += 5
        if re.search(r'[A-Z][a-z]+', content):
            info_score += 5
        if re.search(r'http[s]?://|www\.', content):
            info_score += 5

        quality_score += min(info_score, 30)

        return min(quality_score, 100)

    def assess_value(self, content: str) -> int:
        """
        评估价值 (0-100)

        评估维度：
        - 实用价值：用户偏好、具体事实
        - 情感价值：感谢、倾诉
        - 未来价值：学习需求

        Args:
            content: 要评估的内容

        Returns:
            int: 价值分数 (0-100)
        """
        value_score = 30  # 基础分
        content_lower = content.lower()

        # 实用价值 (0-40分)
        practical_score = 0

        # 检查是否匹配用户偏好
        if self.selector:
            try:
                preferences = self.selector.get_user_preferences()
                for pref in preferences:
                    if pref.lower() in content_lower:
                        practical_score += 10
            except:
                pass

        # 具体事实检测
        fact_indicators = [
            '是', '有', '在', '可以', '需要', '应该',
            '方法', '步骤', '原因', '结果', '例如'
        ]
        fact_count = sum(1 for indicator in fact_indicators
                        if indicator in content)
        practical_score += min(fact_count * 2, 15)

        # 教程/指南类内容
        tutorial_patterns = ['如何', '怎么', '教程', '指南', '步骤', '方法']
        if any(pattern in content for pattern in tutorial_patterns):
            practical_score += 10

        value_score += min(practical_score, 40)

        # 情感价值 (0-30分)
        emotional_score = 0

        # 感谢表达
        gratitude_words = ['谢谢', '感谢', ' helpful', '谢谢', 'thank']
        if any(word in content_lower for word in gratitude_words):
            emotional_score += 15

        # 倾诉/分享
        sharing_words = ['我觉得', '我认为', '我的经验', '分享', '经历']
        if any(word in content for word in sharing_words):
            emotional_score += 10

        # 情感词汇
        emotion_words = ['开心', '难过', '喜欢', '讨厌', '爱', '恨', '感动']
        emotion_count = sum(1 for word in emotion_words if word in content)
        emotional_score += min(emotion_count * 3, 10)

        value_score += min(emotional_score, 30)

        # 未来价值 (0-30分)
        future_score = 0

        # 学习需求
        learning_words = ['学习', '了解', '掌握', '提高', '进步', '技能']
        if any(word in content for word in learning_words):
            future_score += 15

        # 问题/疑问（有学习潜力）
        question_words = ['为什么', '是什么', '怎么做', '如何', '疑问']
        if any(word in content for word in question_words):
            future_score += 10

        # 知识性内容
        knowledge_indicators = ['知识', '理论', '原理', '概念', '定义']
        if any(word in content for word in knowledge_indicators):
            future_score += 10

        value_score += min(future_score, 30)

        return min(value_score, 100)

    def _get_risk_level(self, privacy_risk: int, security_risk: int) -> str:
        """
        根据隐私和安全风险确定风险等级

        Args:
            privacy_risk: 隐私风险分数
            security_risk: 安全风险分数

        Returns:
            str: 风险等级
        """
        max_risk = max(privacy_risk, security_risk)

        if max_risk >= self.RISK_THRESHOLDS['critical']:
            return 'critical'
        elif max_risk >= self.RISK_THRESHOLDS['high']:
            return 'high'
        elif max_risk >= self.RISK_THRESHOLDS['medium']:
            return 'medium'
        elif max_risk >= self.RISK_THRESHOLDS['low']:
            return 'low'
        else:
            return 'minimal'

    def make_judgment(self, content: str) -> Dict[str, Any]:
        """
        综合判断 - 做出学习、存储和加密决策

        Args:
            content: 要判断的内容

        Returns:
            Dict: 决策结果字典
        """
        # 获取各项评估分数
        privacy_risk = self.assess_privacy_risk(content)
        security_risk = self.assess_security_risk(content)
        quality = self.assess_quality(content)
        value = self.assess_value(content)

        # 确定风险等级
        risk_level = self._get_risk_level(privacy_risk, security_risk)

        # 决策逻辑
        should_learn = False
        should_store = False
        should_encrypt = False
        reasons = []

        # 加密决策：隐私风险高时需要加密
        if privacy_risk >= 70:
            should_encrypt = True
            reasons.append(f"隐私风险较高({privacy_risk}分)，建议加密存储")

        # 存储决策：质量或价值足够且安全风险不高
        if security_risk < 80 and (quality >= 40 or value >= 50):
            should_store = True
            if quality >= 40:
                reasons.append(f"内容质量良好({quality}分)")
            if value >= 50:
                reasons.append(f"内容价值较高({value}分)")
        else:
            if security_risk >= 80:
                reasons.append(f"安全风险过高({security_risk}分)，不建议存储")
            if quality < 40 and value < 50:
                reasons.append("内容质量和价值较低")

        # 学习决策：综合评估
        if risk_level in ['critical', 'high']:
            should_learn = False
            reasons.append(f"风险等级为{risk_level}，不适合学习")
        elif quality >= 50 and value >= 40 and security_risk < 70:
            should_learn = True
            reasons.append("内容质量、价值达标且风险可控，适合学习")
        elif value >= 70 and security_risk < 60:
            should_learn = True
            reasons.append("内容价值很高，适合学习")
        else:
            reasons.append("未达到学习标准")

        # 构建结果
        result = {
            'should_learn': should_learn,
            'should_store': should_store,
            'should_encrypt': should_encrypt,
            'risk_level': risk_level,
            'reason': '；'.join(reasons) if reasons else '无特殊说明',
            'scores': {
                'privacy_risk': privacy_risk,
                'security_risk': security_risk,
                'quality': quality,
                'value': value
            }
        }

        return result

    def analyze(self, content: str) -> Dict[str, Any]:
        """
        完整分析 - 返回所有评估维度的详细结果

        Args:
            content: 要分析的内容

        Returns:
            Dict: 完整的分析结果
        """
        # 获取各项评估
        privacy_risk = self.assess_privacy_risk(content)
        security_risk = self.assess_security_risk(content)
        quality = self.assess_quality(content)
        value = self.assess_value(content)

        # 获取决策结果
        judgment = self.make_judgment(content)

        # 构建详细分析结果
        analysis = {
            'content_summary': content[:100] + '...' if len(content) > 100 else content,
            'assessments': {
                'privacy_risk': {
                    'score': privacy_risk,
                    'level': self._get_risk_level(privacy_risk, 0),
                    'description': self._get_privacy_risk_description(privacy_risk)
                },
                'security_risk': {
                    'score': security_risk,
                    'level': self._get_risk_level(0, security_risk),
                    'description': self._get_security_risk_description(security_risk)
                },
                'quality': {
                    'score': quality,
                    'level': self._get_quality_level(quality),
                    'description': self._get_quality_description(quality)
                },
                'value': {
                    'score': value,
                    'level': self._get_value_level(value),
                    'description': self._get_value_description(value)
                }
            },
            'judgment': judgment,
            'recommendations': self._generate_recommendations(
                privacy_risk, security_risk, quality, value, judgment
            )
        }

        return analysis

    def _get_privacy_risk_description(self, score: int) -> str:
        """获取隐私风险描述"""
        if score >= 90:
            return "包含极高风险隐私信息（银行卡/密码/身份证号）"
        elif score >= 80:
            return "包含高风险隐私信息（手机号等联系方式）"
        elif score >= 50:
            return "包含中等风险隐私信息（邮箱/地址）"
        elif score >= 30:
            return "包含低风险隐私信息（个人信息）"
        else:
            return "未发现明显隐私风险"

    def _get_security_risk_description(self, score: int) -> str:
        """获取安全风险描述"""
        if score >= 80:
            return "包含严重安全威胁（恶意代码/攻击指令）"
        elif score >= 60:
            return "包含较高安全风险（攻击性内容/敏感话题）"
        elif score >= 40:
            return "包含一定安全风险"
        elif score >= 20:
            return "包含轻微安全风险"
        else:
            return "未发现明显安全风险"

    def _get_quality_level(self, score: int) -> str:
        """获取质量等级"""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'acceptable'
        elif score >= 20:
            return 'poor'
        else:
            return 'very_poor'

    def _get_quality_description(self, score: int) -> str:
        """获取质量描述"""
        if score >= 80:
            return "内容质量优秀，结构清晰，信息丰富"
        elif score >= 60:
            return "内容质量良好，表达清晰"
        elif score >= 40:
            return "内容质量可接受"
        elif score >= 20:
            return "内容质量较差"
        else:
            return "内容质量很差或为空"

    def _get_value_level(self, score: int) -> str:
        """获取价值等级"""
        if score >= 80:
            return 'very_high'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score >= 20:
            return 'low'
        else:
            return 'very_low'

    def _get_value_description(self, score: int) -> str:
        """获取价值描述"""
        if score >= 80:
            return "具有很高价值，建议重点学习"
        elif score >= 60:
            return "具有较高价值，值得学习"
        elif score >= 40:
            return "具有一定价值"
        elif score >= 20:
            return "价值较低"
        else:
            return "几乎没有学习价值"

    def _generate_recommendations(self, privacy_risk: int, security_risk: int,
                                  quality: int, value: int,
                                  judgment: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于隐私风险的建议
        if privacy_risk >= 90:
            recommendations.append("强烈建议：内容包含敏感信息，必须加密存储")
        elif privacy_risk >= 70:
            recommendations.append("建议：对敏感信息进行加密处理")

        # 基于安全风险的建议
        if security_risk >= 80:
            recommendations.append("警告：内容可能包含安全威胁，谨慎处理")
        elif security_risk >= 60:
            recommendations.append("注意：内容存在一定安全风险")

        # 基于质量的建议
        if quality < 40:
            recommendations.append("建议：提升内容质量和表达清晰度")

        # 基于决策的建议
        if judgment['should_learn']:
            recommendations.append("建议：该内容适合用于模型学习")
        else:
            recommendations.append("建议：暂不适合学习，可考虑优化后重新评估")

        if not judgment['should_store']:
            recommendations.append("建议：考虑是否值得存储该内容")

        return recommendations
