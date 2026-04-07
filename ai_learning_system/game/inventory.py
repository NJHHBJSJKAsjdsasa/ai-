"""物品背包系统

重新设计的背包系统，提供更清晰、更强大的物品管理功能。
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class InventoryItem:
    """背包物品数据类"""
    name: str  # 物品名称
    count: int  # 数量
    item_data: Dict[str, Any]  # 物品详细数据
    stackable: bool = True  # 是否可堆叠
    max_stack: int = 99  # 最大堆叠数量
    usable: bool = True  # 是否可使用


class Inventory:
    """玩家背包系统"""
    
    def __init__(self, max_slots: int = 50):
        """
        初始化背包
        
        Args:
            max_slots: 背包最大槽位数量
        """
        self.max_slots = max_slots
        self.items: Dict[str, InventoryItem] = {}  # {item_name: InventoryItem}
        self.generated_items: Dict[str, Dict[str, Any]] = {}  # 存储动态生成的道具定义
    
    def add_item(self, item_name: str, count: int = 1, item_data: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        添加道具到背包
        
        Args:
            item_name: 道具名称
            count: 数量
            item_data: 道具详细数据
        
        Returns:
            (是否成功, 消息)
        """
        # 检查背包空间
        if item_name not in self.items and len(self.items) >= self.max_slots:
            return False, "背包已满"
        
        # 检查是否是生成道具
        if item_name not in self.items and item_data:
            # 存储生成道具定义
            self.generated_items[item_name] = item_data
        
        # 检查是否可堆叠
        if item_name in self.items:
            item = self.items[item_name]
            if item.stackable:
                new_count = item.count + count
                if new_count <= item.max_stack:
                    item.count = new_count
                    return True, f"获得 {item_name} x{count}"
                else:
                    return False, f"{item_name} 堆叠数量已达上限"
            else:
                return False, f"{item_name} 不可堆叠"
        else:
            # 新物品
            if not item_data:
                # 尝试从生成道具中获取数据
                item_data = self.generated_items.get(item_name, {})
            
            stackable = item_data.get('stackable', True)
            max_stack = item_data.get('max_stack', 99)
            usable = item_data.get('usable', True)
            
            self.items[item_name] = InventoryItem(
                name=item_name,
                count=count,
                item_data=item_data,
                stackable=stackable,
                max_stack=max_stack,
                usable=usable
            )
            return True, f"获得 {item_name} x{count}"
    
    def add_generated_item(self, item_name: str, item_data: Dict[str, Any], count: int = 1) -> Tuple[bool, str]:
        """
        添加动态生成的道具
        
        Args:
            item_name: 道具名称
            item_data: 道具数据
            count: 数量
        
        Returns:
            (是否成功, 消息)
        """
        # 存储生成道具定义
        self.generated_items[item_name] = item_data
        
        # 添加到背包
        return self.add_item(item_name, count, item_data)
    
    def remove_item(self, item_name: str, count: int = 1) -> Tuple[bool, str]:
        """
        从背包中移除道具
        
        Args:
            item_name: 道具名称
            count: 数量
        
        Returns:
            (是否成功, 消息)
        """
        if item_name not in self.items:
            return False, f"背包中没有 {item_name}"
        
        item = self.items[item_name]
        if item.count < count:
            return False, f"{item_name} 数量不足"
        
        item.count -= count
        if item.count <= 0:
            del self.items[item_name]
            # 保留生成道具定义，以便下次添加时使用
        
        return True, f"移除了 {item_name} x{count}"
    
    def use_item(self, item_name: str, count: int = 1) -> Tuple[bool, str]:
        """
        使用道具
        
        Args:
            item_name: 道具名称
            count: 使用数量
        
        Returns:
            (是否成功, 消息)
        """
        if item_name not in self.items:
            return False, f"背包中没有 {item_name}"
        
        item = self.items[item_name]
        if not item.usable:
            return False, f"{item_name} 无法使用"
        
        if item.count < count:
            return False, f"{item_name} 数量不足"
        
        # 移除道具
        success, message = self.remove_item(item_name, count)
        if success:
            return True, f"使用了 {item_name} x{count}"
        return False, message
    
    def get_item_count(self, item_name: str) -> int:
        """
        获取道具数量
        
        Args:
            item_name: 道具名称
        
        Returns:
            道具数量
        """
        if item_name in self.items:
            return self.items[item_name].count
        return 0
    
    def get_item_data(self, item_name: str) -> Optional[Dict[str, Any]]:
        """
        获取道具数据
        
        Args:
            item_name: 道具名称
        
        Returns:
            道具数据，如果不存在返回None
        """
        if item_name in self.items:
            return self.items[item_name].item_data
        return self.generated_items.get(item_name)
    
    def get_total_value(self) -> int:
        """
        获取背包总价值
        
        Returns:
            总价值（灵石）
        """
        total = 0
        for item in self.items.values():
            value = item.item_data.get('value', 100)
            total += value * item.count
        return total
    
    def is_full(self) -> bool:
        """
        检查背包是否已满
        
        Returns:
            是否已满
        """
        return len(self.items) >= self.max_slots
    
    def get_items_by_type(self, item_type: str) -> Dict[str, InventoryItem]:
        """
        按类型获取背包中的道具
        
        Args:
            item_type: 道具类型
        
        Returns:
            道具字典
        """
        result = {}
        for item_name, item in self.items.items():
            if item.item_data.get('type') == item_type:
                result[item_name] = item
        return result
    
    def sort_items(self, sort_by: str = "value", reverse: bool = True) -> List[Tuple[str, InventoryItem]]:
        """
        排序背包中的道具
        
        Args:
            sort_by: 排序依据 (value, name, count, rarity)
            reverse: 是否降序
        
        Returns:
            排序后的道具列表
        """
        items_list = []
        for item_name, item in self.items.items():
            item_data = item.item_data
            if sort_by == "value":
                key = item_data.get('value', 0)
            elif sort_by == "name":
                key = item_name
            elif sort_by == "count":
                key = item.count
            elif sort_by == "rarity":
                rarity_order = {"普通": 1, "优秀": 2, "稀有": 3, "史诗": 4, "传说": 5, "神话": 6}
                key = rarity_order.get(item_data.get('rarity', "普通"), 1)
            else:
                key = 0
            items_list.append((item_name, item, key))
        
        items_list.sort(key=lambda x: x[2], reverse=reverse)
        return [(item[0], item[1]) for item in items_list]
    
    def organize(self):
        """
        整理背包
        按类型和稀有度排序，优化空间使用
        """
        # 先按类型分组
        items_by_type = {}
        for item_name, item in self.items.items():
            item_type = item.item_data.get('type', '其他')
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append((item_name, item))
        
        # 按稀有度和价值排序每个类型的道具
        sorted_items = {}
        for item_type, items in items_by_type.items():
            # 按稀有度和价值排序
            items.sort(key=lambda x: (
                {"普通": 1, "优秀": 2, "稀有": 3, "史诗": 4, "传说": 5, "神话": 6}.get(x[1].item_data.get('rarity', "普通"), 1),
                x[1].item_data.get('value', 0)
            ), reverse=True)
            for item_name, item in items:
                sorted_items[item_name] = item
        
        # 更新背包
        self.items = sorted_items
    
    def search(self, keyword: str) -> Dict[str, InventoryItem]:
        """
        在背包中搜索道具
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的道具字典
        """
        result = {}
        keyword_lower = keyword.lower()
        for item_name, item in self.items.items():
            if (keyword_lower in item_name.lower() or 
                keyword_lower in item.item_data.get('description', '').lower() or
                any(keyword_lower in effect.lower() for effect in item.item_data.get('effects', []))):
                result[item_name] = item
        return result
    
    def clear(self):
        """
        清空背包
        """
        self.items.clear()
        # 保留生成道具定义
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典，用于保存到数据库
        
        Returns:
            背包数据字典
        """
        items_dict = {}
        for item_name, item in self.items.items():
            items_dict[item_name] = {
                "count": item.count,
                "data": item.item_data,
                "stackable": item.stackable,
                "max_stack": item.max_stack,
                "usable": item.usable
            }
        
        return {
            "items": items_dict,
            "generated_items": self.generated_items,
            "max_slots": self.max_slots
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """
        从字典加载背包数据
        
        Args:
            data: 背包数据字典
        """
        if not isinstance(data, dict):
            return
        
        # 加载物品
        items_data = data.get('items', {})
        self.items = {}
        for item_name, item_info in items_data.items():
            self.items[item_name] = InventoryItem(
                name=item_name,
                count=item_info.get('count', 1),
                item_data=item_info.get('data', {}),
                stackable=item_info.get('stackable', True),
                max_stack=item_info.get('max_stack', 99),
                usable=item_info.get('usable', True)
            )
        
        # 加载生成的道具定义
        self.generated_items = data.get('generated_items', {})
        
        # 加载背包容量
        self.max_slots = data.get('max_slots', 50)
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """
        获取背包摘要信息
        
        Returns:
            背包摘要信息
        """
        summary = {
            "total_items": len(self.items),
            "max_slots": self.max_slots,
            "total_value": self.get_total_value(),
            "items_by_type": {},
            "empty_slots": self.max_slots - len(self.items)
        }
        
        # 按类型统计
        for item_name, item in self.items.items():
            item_type = item.item_data.get('type', '其他')
            if item_type not in summary['items_by_type']:
                summary['items_by_type'][item_type] = 0
            summary['items_by_type'][item_type] += 1
        
        return summary
