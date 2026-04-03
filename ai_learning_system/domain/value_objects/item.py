class Item:
    def __init__(self, id, name, type, rarity, effects):
        self.id = id
        self.name = name
        self.type = type
        self.rarity = rarity
        self.effects = effects
    
    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return self.id == other.id
    
    def use(self, target):
        # 使用物品逻辑
        pass
