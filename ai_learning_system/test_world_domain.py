"""
世界领域模型测试文件
"""

import pytest
from domain.entities.world import World
from domain.entities.location import Location
from domain.value_objects.time import GameTime
from domain.value_objects.location import LocationValue, GeneratedLocationValue
from domain.services.world_service import WorldService
from domain.services.time_service import RealTimeSystem


class TestWorldDomain:
    """世界领域模型测试类"""
    
    def test_game_time_creation(self):
        """测试GameTime值对象的创建"""
        game_time = GameTime(year=1, month=1, day=1, hour=8)
        assert game_time.year == 1
        assert game_time.month == 1
        assert game_time.day == 1
        assert game_time.hour == 8
    
    def test_game_time_advance(self):
        """测试GameTime的时间推进功能"""
        game_time = GameTime(year=1, month=1, day=1, hour=23)
        new_time = game_time.advance(2)
        assert new_time.year == 1
        assert new_time.month == 1
        assert new_time.day == 2
        assert new_time.hour == 1
    
    def test_game_time_to_string(self):
        """测试GameTime的字符串转换功能"""
        game_time = GameTime(year=1, month=1, day=1, hour=9)
        assert "清晨" in game_time.to_string()
    
    def test_location_value_creation(self):
        """测试LocationValue值对象的创建"""
        location_value = LocationValue(
            name="新手村",
            description="凡人居住的村落",
            realm_required=0
        )
        assert location_value.name == "新手村"
        assert location_value.description == "凡人居住的村落"
        assert location_value.realm_required == 0
    
    def test_location_value_accessibility(self):
        """测试LocationValue的可访问性检查"""
        location_value = LocationValue(
            name="黄枫谷",
            description="越国七大派之一",
            realm_required=1
        )
        assert location_value.is_accessible(1) is True
        assert location_value.is_accessible(0) is False
    
    def test_location_creation(self):
        """测试Location实体的创建"""
        location_value = LocationValue(
            name="新手村",
            description="凡人居住的村落",
            realm_required=0
        )
        location = Location(name="新手村", location_value=location_value)
        assert location.name == "新手村"
        assert location.location_value == location_value
    
    def test_location_add_connection(self):
        """测试Location实体的添加连接功能"""
        location_value = LocationValue(
            name="新手村",
            description="凡人居住的村落",
            realm_required=0
        )
        location = Location(name="新手村", location_value=location_value)
        location.add_connection("彩霞山")
        assert "彩霞山" in location.location_value.connections
    
    def test_world_creation(self):
        """测试World实体的创建"""
        world = World(id="world_1", name="修仙世界")
        assert world.id == "world_1"
        assert world.name == "修仙世界"
        assert len(world.locations) == 0
    
    def test_world_add_location(self):
        """测试World实体的添加地点功能"""
        world = World(id="world_1", name="修仙世界")
        location_value = LocationValue(
            name="新手村",
            description="凡人居住的村落",
            realm_required=0
        )
        location = Location(name="新手村", location_value=location_value)
        world.add_location(location)
        assert "新手村" in world.locations
    
    def test_world_connect_locations(self):
        """测试World实体的连接地点功能"""
        world = World(id="world_1", name="修仙世界")
        
        # 添加两个地点
        loc1_value = LocationValue(
            name="新手村",
            description="凡人居住的村落",
            realm_required=0
        )
        loc1 = Location(name="新手村", location_value=loc1_value)
        world.add_location(loc1)
        
        loc2_value = LocationValue(
            name="彩霞山",
            description="七玄门所在之地",
            realm_required=0
        )
        loc2 = Location(name="彩霞山", location_value=loc2_value)
        world.add_location(loc2)
        
        # 连接两个地点
        result = world.connect_locations("新手村", "彩霞山")
        assert result is True
        assert "彩霞山" in world.locations["新手村"].location_value.connections
        assert "新手村" in world.locations["彩霞山"].location_value.connections
    
    def test_world_service_initialize(self):
        """测试WorldService的初始化世界功能"""
        world_service = WorldService()
        world = world_service.initialize_world("world_1", "修仙世界")
        assert world.id == "world_1"
        assert world.name == "修仙世界"
        assert len(world.locations) > 0
    
    def test_world_service_can_enter(self):
        """测试WorldService的进入地点检查功能"""
        world_service = WorldService()
        world = world_service.initialize_world("world_1", "修仙世界")
        
        # 测试可进入的地点
        assert world_service.can_enter(world, "新手村", 0) is True
        
        # 测试不可进入的地点
        assert world_service.can_enter(world, "黄枫谷", 0) is False
    
    def test_world_service_get_accessible_locations(self):
        """测试WorldService的获取可到达地点功能"""
        world_service = WorldService()
        world = world_service.initialize_world("world_1", "修仙世界")
        
        # 测试凡人可到达的地点
        accessible = world.get_accessible_locations("新手村", 0)
        assert len(accessible) > 0
    
    def test_world_advance_time(self):
        """测试World的时间推进功能"""
        world = World(id="world_1", name="修仙世界")
        initial_time = world.get_current_time()
        world.advance_time(24)
        updated_time = world.get_current_time()
        assert updated_time.day > initial_time.day
    
    def test_real_time_system_update(self):
        """测试RealTimeSystem的时间更新功能"""
        time_system = RealTimeSystem()
        initial_time = time_system.get_game_time()
        # 模拟时间更新
        time_system.update()
        updated_time = time_system.get_game_time()
        assert updated_time.year >= initial_time.year
    
    def test_generated_location_value(self):
        """测试GeneratedLocationValue值对象"""
        generated_location = GeneratedLocationValue(
            id="gen_1",
            name="神秘洞穴",
            description="一个神秘的洞穴",
            realm_required=2,
            map_type="洞穴",
            level=3
        )
        assert generated_location.id == "gen_1"
        assert generated_location.name == "神秘洞穴"
        assert generated_location.realm_required == 2
        assert generated_location.map_type == "洞穴"
        assert generated_location.level == 3


if __name__ == "__main__":
    pytest.main([__file__])