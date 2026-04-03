import pytest
from unittest.mock import Mock, MagicMock
from domain.entities.player import Player
from domain.services.cultivation_service import CultivationService as DomainCultivationService
from domain.repositories.player_repository import PlayerRepository
from application.services.cultivation_service import CultivationService
from application.commands.cultivation_commands import CultivateCommand, AttemptBreakthroughCommand
from application.queries.cultivation_queries import GetCultivationStatusQuery
from application.handlers.cultivation_command_handler import CultivationCommandHandler
from application.handlers.cultivation_query_handler import CultivationQueryHandler
from application.use_cases.cultivation_use_case import CultivationUseCase

class TestCultivationApplication:
    """测试修炼应用层"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建模拟对象
        self.mock_domain_cultivation_service = Mock(spec=DomainCultivationService)
        self.mock_player_repository = Mock(spec=PlayerRepository)
        self.mock_player = Mock(spec=Player)
        
        # 配置模拟对象
        self.mock_player_repository.find_by_id.return_value = self.mock_player
        self.mock_domain_cultivation_service.calculate_cultivation_progress.return_value = 100
        self.mock_domain_cultivation_service.check_breakthrough.return_value = False
        self.mock_domain_cultivation_service.perform_breakthrough.return_value = True
        self.mock_domain_cultivation_service.get_cultivation_status.return_value = {
            "current_realm": "练气期",
            "current_exp": 500,
            "required_exp": 1000,
            "progress": 0.5,
            "next_realm": "筑基期"
        }
    
    def test_cultivation_command_handler_handle_cultivate(self):
        """测试修炼命令处理程序处理修炼命令"""
        # 创建命令处理程序
        command_handler = CultivationCommandHandler(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 创建命令
        command = CultivateCommand(player_id="player1", time_spent=1)
        
        # 执行命令
        result = command_handler.handle_cultivate(command)
        
        # 验证结果
        assert result is not None
        assert result["gained_exp"] == 100
        assert result["breakthrough"] is False
        self.mock_domain_cultivation_service.calculate_cultivation_progress.assert_called_once_with(self.mock_player, 1)
        self.mock_player_repository.update.assert_called_once_with(self.mock_player)
    
    def test_cultivation_command_handler_handle_attempt_breakthrough(self):
        """测试修炼命令处理程序处理尝试突破命令"""
        # 创建命令处理程序
        command_handler = CultivationCommandHandler(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 创建命令
        command = AttemptBreakthroughCommand(player_id="player1")
        
        # 执行命令
        result = command_handler.handle_attempt_breakthrough(command)
        
        # 验证结果
        assert result is not None
        assert result["breakthrough"] is True
        self.mock_domain_cultivation_service.perform_breakthrough.assert_called_once_with(self.mock_player)
        self.mock_player_repository.update.assert_called_once_with(self.mock_player)
    
    def test_cultivation_query_handler_handle_get_cultivation_status(self):
        """测试修炼查询处理程序处理获取修炼状态查询"""
        # 创建查询处理程序
        query_handler = CultivationQueryHandler(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 创建查询
        query = GetCultivationStatusQuery(player_id="player1")
        
        # 执行查询
        result = query_handler.handle_get_cultivation_status(query)
        
        # 验证结果
        assert result is not None
        assert result["current_realm"] == "练气期"
        self.mock_domain_cultivation_service.get_cultivation_status.assert_called_once_with(self.mock_player)
    
    def test_cultivation_service_cultivate(self):
        """测试修炼应用服务执行修炼"""
        # 创建应用服务
        cultivation_service = CultivationService(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 执行修炼
        result = cultivation_service.cultivate(player_id="player1", time_spent=1)
        
        # 验证结果
        assert result is not None
        assert result["gained_exp"] == 100
    
    def test_cultivation_service_attempt_breakthrough(self):
        """测试修炼应用服务尝试突破"""
        # 创建应用服务
        cultivation_service = CultivationService(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 尝试突破
        result = cultivation_service.attempt_breakthrough(player_id="player1")
        
        # 验证结果
        assert result is not None
        assert result["breakthrough"] is True
    
    def test_cultivation_service_get_cultivation_status(self):
        """测试修炼应用服务获取修炼状态"""
        # 创建应用服务
        cultivation_service = CultivationService(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 获取修炼状态
        result = cultivation_service.get_cultivation_status(player_id="player1")
        
        # 验证结果
        assert result is not None
        assert result["current_realm"] == "练气期"
    
    def test_cultivation_use_case_execute(self):
        """测试修炼用例执行修炼"""
        # 创建应用服务
        cultivation_service = CultivationService(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 创建用例
        use_case = CultivationUseCase(cultivation_service)
        
        # 执行用例
        result = use_case.execute(player_id="player1", time_spent=1)
        
        # 验证结果
        assert result is not None
        assert result["gained_exp"] == 100
    
    def test_cultivation_use_case_get_cultivation_status(self):
        """测试修炼用例获取修炼状态"""
        # 创建应用服务
        cultivation_service = CultivationService(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 创建用例
        use_case = CultivationUseCase(cultivation_service)
        
        # 获取修炼状态
        result = use_case.get_cultivation_status(player_id="player1")
        
        # 验证结果
        assert result is not None
        assert result["current_realm"] == "练气期"
    
    def test_cultivation_use_case_attempt_breakthrough(self):
        """测试修炼用例尝试突破"""
        # 创建应用服务
        cultivation_service = CultivationService(
            self.mock_domain_cultivation_service, 
            self.mock_player_repository
        )
        
        # 创建用例
        use_case = CultivationUseCase(cultivation_service)
        
        # 尝试突破
        result = use_case.attempt_breakthrough(player_id="player1")
        
        # 验证结果
        assert result is not None
        assert result["breakthrough"] is True
