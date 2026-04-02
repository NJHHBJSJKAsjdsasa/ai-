# 完整记忆管理器实现规范

## Why
当前 `main.py` 中使用的是简化版的记忆管理器（MemoryManager 占位类），功能有限，只提供基本的记忆增删改查。需要实现完整的记忆管理器，提供隐私检测、重要性评分、记忆选择、加密存储等高级功能。

## What Changes
- **替换** `main.py` 中的简化版 MemoryManager 为完整版
- **新增** 导入完整记忆管理器所需的依赖（Selector, PrivacyDetector）
- **修改** `main.py` 的初始化逻辑，正确初始化完整的记忆管理器
- **保留** 原有的数据库交互接口兼容性

## Impact
- 受影响代码：`main.py` 中的 MemoryManager 类定义和初始化逻辑
- 新增依赖：`core/selector.py`, `utils/privacy_detector.py`
- 功能增强：隐私检测、重要性评分、记忆加密、自动遗忘等

## ADDED Requirements

### Requirement: 完整记忆管理功能
系统 SHALL 提供完整的记忆管理功能，包括隐私保护、重要性评估、智能存储。

#### Scenario: 隐私保护
- **WHEN** 用户输入包含敏感信息
- **THEN** 系统应该自动检测并加密存储

#### Scenario: 重要性评估
- **WHEN** 添加新记忆
- **THEN** 系统应该评估重要性，低重要性内容可选择不存储

#### Scenario: 记忆检索
- **WHEN** 搜索记忆
- **THEN** 系统应该返回相关的记忆内容

## MODIFIED Requirements
### Requirement: MemoryManager 初始化
修改 `main.py` 中的初始化逻辑，使用完整的 MemoryManager。

## REMOVED Requirements
无
