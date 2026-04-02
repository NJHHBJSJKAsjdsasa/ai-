#!/usr/bin/env python3
"""
凡人修仙传小说数据导入脚本
一键导入小说数据到游戏配置
"""

import sys
import json
from pathlib import Path
from typing import Dict, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.novel_parser import NovelParser, get_novel_data
from config import (
    SECTS, SECT_DETAILS, SECT_RELATIONSHIPS,
    TECHNIQUES_DB, ITEMS_DB, FANREN_CHARACTERS
)


class NovelDataImporter:
    """小说数据导入器"""
    
    def __init__(self, novel_path: str = None):
        self.parser = NovelParser(novel_path)
        self.report = {
            "sects": {"added": 0, "updated": 0, "errors": []},
            "techniques": {"added": 0, "updated": 0, "errors": []},
            "items": {"added": 0, "updated": 0, "errors": []},
            "characters": {"added": 0, "updated": 0, "errors": []},
        }
    
    def import_all(self) -> Dict:
        """
        导入所有小说数据
        
        Returns:
            导入报告
        """
        print("=" * 60)
        print("凡人修仙传小说数据导入")
        print("=" * 60)
        
        # 获取小说数据
        novel_data = self.parser._get_all_predefined()
        
        # 导入门派数据
        self._import_sects(novel_data.get("sects", {}))
        
        # 导入功法数据
        self._import_techniques(novel_data.get("techniques", {}))
        
        # 导入道具数据
        self._import_items(novel_data.get("items", {}))
        
        # 导入角色数据
        self._import_characters(novel_data.get("characters", {}))
        
        return self.report
    
    def _import_sects(self, sects_data: Dict):
        """导入门派数据"""
        print("\n【导入门派数据】")
        
        for name, data in sects_data.items():
            try:
                if name in SECTS:
                    print(f"  ✓ 门派已存在: {name}")
                    self.report["sects"]["updated"] += 1
                else:
                    print(f"  + 新增门派: {name}")
                    SECTS.append(name)
                    self.report["sects"]["added"] += 1
                
                # 更新详细信息
                if name not in SECT_DETAILS:
                    SECT_DETAILS[name] = data
                    
            except Exception as e:
                self.report["sects"]["errors"].append(f"{name}: {str(e)}")
                print(f"  ✗ 导入失败: {name} - {e}")
        
        print(f"  总计: {self.report['sects']['added']} 新增, {self.report['sects']['updated']} 更新")
    
    def _import_techniques(self, techniques_data: Dict):
        """导入功法数据"""
        print("\n【导入功法数据】")
        
        for name, data in techniques_data.items():
            try:
                if name in TECHNIQUES_DB:
                    print(f"  ✓ 功法已存在: {name}")
                    self.report["techniques"]["updated"] += 1
                else:
                    print(f"  + 新增功法: {name}")
                    self.report["techniques"]["added"] += 1
                    
            except Exception as e:
                self.report["techniques"]["errors"].append(f"{name}: {str(e)}")
                print(f"  ✗ 导入失败: {name} - {e}")
        
        print(f"  总计: {self.report['techniques']['added']} 新增, {self.report['techniques']['updated']} 更新")
    
    def _import_items(self, items_data: Dict):
        """导入道具数据"""
        print("\n【导入道具数据】")
        
        for name, data in items_data.items():
            try:
                if name in ITEMS_DB:
                    print(f"  ✓ 道具已存在: {name}")
                    self.report["items"]["updated"] += 1
                else:
                    print(f"  + 新增道具: {name}")
                    self.report["items"]["added"] += 1
                    
            except Exception as e:
                self.report["items"]["errors"].append(f"{name}: {str(e)}")
                print(f"  ✗ 导入失败: {name} - {e}")
        
        print(f"  总计: {self.report['items']['added']} 新增, {self.report['items']['updated']} 更新")
    
    def _import_characters(self, characters_data: Dict):
        """导入角色数据"""
        print("\n【导入角色数据】")
        
        for name, data in characters_data.items():
            try:
                if name in FANREN_CHARACTERS:
                    print(f"  ✓ 角色已存在: {name}")
                    self.report["characters"]["updated"] += 1
                else:
                    print(f"  + 新增角色: {name}")
                    self.report["characters"]["added"] += 1
                    
            except Exception as e:
                self.report["characters"]["errors"].append(f"{name}: {str(e)}")
                print(f"  ✗ 导入失败: {name} - {e}")
        
        print(f"  总计: {self.report['characters']['added']} 新增, {self.report['characters']['updated']} 更新")
    
    def generate_report(self) -> str:
        """生成导入报告"""
        report_lines = [
            "=" * 60,
            "导入完成报告",
            "=" * 60,
            "",
            f"【门派】新增: {self.report['sects']['added']}, 更新: {self.report['sects']['updated']}",
            f"【功法】新增: {self.report['techniques']['added']}, 更新: {self.report['techniques']['updated']}",
            f"【道具】新增: {self.report['items']['added']}, 更新: {self.report['items']['updated']}",
            f"【角色】新增: {self.report['characters']['added']}, 更新: {self.report['characters']['updated']}",
            "",
        ]
        
        # 错误报告
        total_errors = (
            len(self.report['sects']['errors']) +
            len(self.report['techniques']['errors']) +
            len(self.report['items']['errors']) +
            len(self.report['characters']['errors'])
        )
        
        if total_errors > 0:
            report_lines.append("【错误】")
            if self.report['sects']['errors']:
                report_lines.append("  门派错误:")
                for error in self.report['sects']['errors']:
                    report_lines.append(f"    - {error}")
            if self.report['techniques']['errors']:
                report_lines.append("  功法错误:")
                for error in self.report['techniques']['errors']:
                    report_lines.append(f"    - {error}")
            if self.report['items']['errors']:
                report_lines.append("  道具错误:")
                for error in self.report['items']['errors']:
                    report_lines.append(f"    - {error}")
            if self.report['characters']['errors']:
                report_lines.append("  角色错误:")
                for error in self.report['characters']['errors']:
                    report_lines.append(f"    - {error}")
        else:
            report_lines.append("✓ 无错误")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def export_to_json(self, output_path: str = "novel_data_export.json"):
        """导出数据到JSON文件"""
        data = {
            "sects": self.parser.get_sects(),
            "techniques": {k: v.to_dict() for k, v in TECHNIQUES_DB.items()},
            "items": {k: v.to_dict() for k, v in ITEMS_DB.items()},
            "characters": self.parser.get_characters(),
            "terms": self.parser.get_terms()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n数据已导出到: {output_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='凡人修仙传小说数据导入工具')
    parser.add_argument('--novel', '-n', type=str, help='小说文件路径')
    parser.add_argument('--export', '-e', type=str, default='novel_data_export.json', 
                        help='导出JSON文件路径')
    parser.add_argument('--dry-run', '-d', action='store_true', 
                        help='试运行，不实际导入数据')
    
    args = parser.parse_args()
    
    # 创建导入器
    importer = NovelDataImporter(args.novel)
    
    # 导入数据
    if args.dry_run:
        print("【试运行模式】不实际导入数据")
    
    report = importer.import_all()
    
    # 显示报告
    print("\n" + importer.generate_report())
    
    # 导出数据
    importer.export_to_json(args.export)
    
    print("\n导入完成！")


if __name__ == "__main__":
    main()
