"""
AI回复智能评判系统
评估AI回复的质量，给予相应的修为奖励
"""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import XIUXIAN_TERMS


class ReplyCategory(Enum):
    """回复分类"""
    CULTIVATION_GUIDE = "cultivation_guide"  # 修炼指导
    WORLD_EXPLANATION = "world_explanation"  # 世界观解释
    STORY_TELLING = "story_telling"          # 故事讲述
    CHARACTER_ROLEPLAY = "character_roleplay" # 角色扮演
    GENERAL_CHAT = "general_chat"            # 普通对话


@dataclass
class JudgeResult:
    """评判结果"""
    score: int                      # 总分 (0-100)
    category: ReplyCategory         # 分类
    xiuxian_term_count: int         # 修仙术语使用数量
    immersion_score: int            # 沉浸感分数
    helpfulness_score: int          # 有用性分数
    creativity_score: int           # 创意分数
    exp_reward: int                 # 修为奖励
    feedback: str                   # 评判反馈


class AIJudgeSystem:
    """AI评判系统"""
    
    def __init__(self):
        """初始化评判系统"""
        self.xiuxian_terms = set()
        for terms in XIUXIAN_TERMS.values():
            self.xiuxian_terms.update([t.lower() for t in terms])
        
        # 评判标准权重
        self.weights = {
            "xiuxian_terms": 0.25,      # 修仙术语使用
            "immersion": 0.30,           # 沉浸感
            "helpfulness": 0.25,         # 有用性
            "creativity": 0.20,          # 创意
        }
    
    def judge(self, user_input: str, ai_reply: str, context: Dict[str, Any] = None) -> JudgeResult:
        """
        评判AI回复
        
        Args:
            user_input: 用户输入
            ai_reply: AI回复
            context: 上下文信息
            
        Returns:
            评判结果
        """
        if context is None:
            context = {}
        
        # 1. 检测修仙术语使用
        xiuxian_count = self._count_xiuxian_terms(ai_reply)
        xiuxian_score = min(25, xiuxian_count * 2)  # 每个术语2分，最高25分
        
        # 2. 评估沉浸感
        immersion_score = self._evaluate_immersion(ai_reply, context)
        
        # 3. 评估有用性
        helpfulness_score = self._evaluate_helpfulness(user_input, ai_reply)
        
        # 4. 评估创意
        creativity_score = self._evaluate_creativity(ai_reply)
        
        # 5. 分类
        category = self._classify_reply(user_input, ai_reply)
        
        # 计算总分
        total_score = (
            xiuxian_score * self.weights["xiuxian_terms"] +
            immersion_score * self.weights["immersion"] +
            helpfulness_score * self.weights["helpfulness"] +
            creativity_score * self.weights["creativity"]
        )
        
        # 计算修为奖励
        exp_reward = self._calculate_exp_reward(
            int(total_score), category, xiuxian_count, context
        )
        
        # 生成反馈
        feedback = self._generate_feedback(
            int(total_score), xiuxian_count, immersion_score, 
            helpfulness_score, creativity_score, category
        )
        
        return JudgeResult(
            score=int(total_score),
            category=category,
            xiuxian_term_count=xiuxian_count,
            immersion_score=immersion_score,
            helpfulness_score=helpfulness_score,
            creativity_score=creativity_score,
            exp_reward=exp_reward,
            feedback=feedback
        )
    
    def _count_xiuxian_terms(self, text: str) -> int:
        """统计修仙术语使用数量"""
        text_lower = text.lower()
        count = 0
        found_terms = set()
        
        for term in self.xiuxian_terms:
            if term in text_lower and term not in found_terms:
                count += text_lower.count(term)
                found_terms.add(term)
        
        return count
    
    def _evaluate_immersion(self, reply: str, context: Dict) -> int:
        """评估沉浸感 (0-100)"""
        score = 50  # 基础分
        
        # 检查是否使用第一人称修仙称谓
        self_titles = ["贫道", "本座", "老夫", "在下", "小修", "本修", "本尊", "本圣", "本仙"]
        if any(title in reply for title in self_titles):
            score += 15
        
        # 检查是否使用第二人称修仙称谓
        other_titles = ["道友", "小友", "道兄", "前辈", "高人"]
        if any(title in reply for title in other_titles):
            score += 15
        
        # 检查是否有古文风格
        classical_patterns = [
            r"[之乎者也矣焉哉]",
            r"[一二三四五六七八九十百千万]+",
            r"(?:修炼|修行|悟道|参悟|打坐|闭关)",
        ]
        for pattern in classical_patterns:
            if re.search(pattern, reply):
                score += 5
                break
        
        # 检查回复长度（适中为佳）
        if 50 <= len(reply) <= 500:
            score += 10
        elif len(reply) > 500:
            score += 5
        
        return min(100, score)
    
    def _evaluate_helpfulness(self, user_input: str, reply: str) -> int:
        """评估有用性 (0-100)"""
        score = 40  # 基础分
        
        # 检查是否回答了问题
        question_words = ["如何", "怎么", "什么", "为什么", "哪里", "谁", "多少"]
        if any(word in user_input for word in question_words):
            # 检查回复是否包含具体信息
            if len(reply) > 30:
                score += 20
            
            # 检查是否给出建议或指导
            guidance_words = ["建议", "可以", "应该", "需要", "必须", "最好"]
            if any(word in reply for word in guidance_words):
                score += 20
        else:
            # 普通对话，检查是否自然流畅
            score += 30
        
        # 检查是否包含具体数值或例子
        if re.search(r"\d+", reply):
            score += 10
        
        return min(100, score)
    
    def _evaluate_creativity(self, reply: str) -> int:
        """评估创意 (0-100)"""
        score = 40  # 基础分
        
        # 检查是否包含故事性描述
        story_patterns = [
            r"(?:曾经|从前|当年|那时|有一日|某日)",
            r"(?:传说|听闻|据说|相传)",
            r"(?:突然|忽然|刹那间|顿时)",
        ]
        for pattern in story_patterns:
            if re.search(pattern, reply):
                score += 20
                break
        
        # 检查是否包含生动的描写
        vivid_words = ["灵气", "霞光", "云雾", "雷霆", "火焰", "冰霜", "金光", "紫气"]
        vivid_count = sum(1 for word in vivid_words if word in reply)
        score += min(20, vivid_count * 4)
        
        # 检查是否包含独特的表达
        unique_phrases = ["大道", "天机", "因果", "轮回", "造化", "机缘", "顿悟"]
        unique_count = sum(1 for phrase in unique_phrases if phrase in reply)
        score += min(20, unique_count * 5)
        
        return min(100, score)
    
    def _classify_reply(self, user_input: str, reply: str) -> ReplyCategory:
        """分类回复"""
        # 根据用户输入和回复内容分类
        cultivation_keywords = ["修炼", "突破", "境界", "功法", "心法", "打坐", "闭关", "灵气"]
        world_keywords = ["世界", "门派", "宗门", "大陆", "仙界", "凡间", "规则"]
        story_keywords = ["故事", "传说", "经历", "往事", "曾经"]
        
        if any(word in user_input for word in cultivation_keywords):
            return ReplyCategory.CULTIVATION_GUIDE
        elif any(word in user_input for word in world_keywords):
            return ReplyCategory.WORLD_EXPLANATION
        elif any(word in user_input for word in story_keywords):
            return ReplyCategory.STORY_TELLING
        elif "道号" in reply or "贫道" in reply or "本座" in reply:
            return ReplyCategory.CHARACTER_ROLEPLAY
        else:
            return ReplyCategory.GENERAL_CHAT
    
    def _calculate_exp_reward(self, score: int, category: ReplyCategory, 
                              xiuxian_count: int, context: Dict) -> int:
        """计算修为奖励"""
        # 基础奖励
        base_exp = score // 10  # 0-10点
        
        # 分类加成
        category_bonus = {
            ReplyCategory.CULTIVATION_GUIDE: 5,
            ReplyCategory.WORLD_EXPLANATION: 3,
            ReplyCategory.STORY_TELLING: 4,
            ReplyCategory.CHARACTER_ROLEPLAY: 3,
            ReplyCategory.GENERAL_CHAT: 1,
        }
        
        bonus = category_bonus.get(category, 1)
        
        # 术语使用加成
        term_bonus = min(5, xiuxian_count)
        
        # 连击加成（如果有连续高质量回复）
        combo_bonus = context.get("combo_count", 0) * 2
        
        total_exp = base_exp + bonus + term_bonus + combo_bonus
        
        # 根据玩家境界调整（境界越高，基础奖励越低）
        realm_level = context.get("realm_level", 0)
        if realm_level >= 5:
            total_exp = int(total_exp * 0.5)
        elif realm_level >= 3:
            total_exp = int(total_exp * 0.7)
        
        return max(1, total_exp)
    
    def _generate_feedback(self, score: int, xiuxian_count: int, 
                          immersion: int, helpfulness: int, 
                          creativity: int, category: ReplyCategory) -> str:
        """生成评判反馈"""
        feedback_parts = []
        
        # 总体评价
        if score >= 90:
            feedback_parts.append("🌟 道韵天成！此回复蕴含大道至理，令人茅塞顿开。")
        elif score >= 75:
            feedback_parts.append("✨ 颇有见地，言辞之间可见修仙底蕴。")
        elif score >= 60:
            feedback_parts.append("👍 中规中矩，尚有提升空间。")
        elif score >= 40:
            feedback_parts.append("😐 平平无奇，缺乏修仙韵味。")
        else:
            feedback_parts.append("💔 道心不稳，需重新参悟。")
        
        # 详细评价
        details = []
        
        if xiuxian_count >= 5:
            details.append(f"术语运用娴熟（{xiuxian_count}处）")
        elif xiuxian_count >= 2:
            details.append(f"术语运用尚可（{xiuxian_count}处）")
        else:
            details.append("术语运用不足")
        
        if immersion >= 80:
            details.append("沉浸感极佳")
        elif immersion >= 60:
            details.append("沉浸感良好")
        else:
            details.append("沉浸感有待提升")
        
        if helpfulness >= 80:
            details.append("极具启发")
        elif helpfulness >= 60:
            details.append("有一定帮助")
        
        if creativity >= 80:
            details.append("创意非凡")
        elif creativity >= 60:
            details.append("颇具巧思")
        
        if details:
            feedback_parts.append(" | ".join(details))
        
        # 分类标签
        category_names = {
            ReplyCategory.CULTIVATION_GUIDE: "【修炼指导】",
            ReplyCategory.WORLD_EXPLANATION: "【世界观】",
            ReplyCategory.STORY_TELLING: "【故事】",
            ReplyCategory.CHARACTER_ROLEPLAY: "【角色扮演】",
            ReplyCategory.GENERAL_CHAT: "【闲聊】",
        }
        feedback_parts.append(category_names.get(category, ""))
        
        return "\n".join(feedback_parts)


# 全局评判实例
judge_system = AIJudgeSystem()


def judge_ai_reply(user_input: str, ai_reply: str, **context) -> JudgeResult:
    """
    便捷函数：评判AI回复
    
    Args:
        user_input: 用户输入
        ai_reply: AI回复
        **context: 上下文信息
        
    Returns:
        评判结果
    """
    return judge_system.judge(user_input, ai_reply, context)
