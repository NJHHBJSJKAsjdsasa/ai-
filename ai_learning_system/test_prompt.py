#!/usr/bin/env python3
"""
测试优化后的提示词构建
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 先检查配置是否可用
from config import XIUXIAN_TERMS
print(f"修仙配置可用，术语数量: {len(XIUXIAN_TERMS)}")

from core.dialogue_engine import DialogueEngine

class MockMemoryManager:
    def get_recent_dialogue(self, limit=5):
        return []
    def search_related_memory(self, message):
        return []
    def get_user_preferences(self):
        return {}

# 创建对话引擎
memory_manager = MockMemoryManager()
engine = DialogueEngine(
    memory_manager=memory_manager,
    model_path=None,
    xiuxian_mode=True,
    dao_name="青云子",
    realm_level=4,
    sect="昆仑派"
)

print(f"修仙模式: {engine.xiuxian_mode}")
print(f"道号: {engine.dao_name}")
print(f"境界: {engine.realm_name}")
print(f"自称: {engine.title_self}")

# 测试提示词构建
test_messages = [
    "你是什么？",
    "天道评判系统是什么？",
]

print('\n' + '=' * 70)
print('优化后的提示词构建测试')
print('=' * 70)

for msg in test_messages:
    print(f'\n用户输入: {msg}')
    print('-' * 70)
    
    context = {
        "user_message": msg,
        "recent_history": [],
        "relevant_memories": [],
        "user_preferences": {}
    }
    
    prompt = engine.build_prompt(msg, context)
    
    # 只显示提示词的前800字符
    print(f'提示词预览:')
    print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
    print()

print('=' * 70)
print('测试完成！')
print('=' * 70)
