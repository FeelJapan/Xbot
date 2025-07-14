"""
ドキュメント自動チェックシステム
このモジュールは、ドキュメントの更新状況を自動的にチェックし、必要な更新を促します。
"""
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json
import re
from ..logging.logger import get_logger
from ..error_handling.error_handler import DocumentError

logger = get_logger("documentation_checker")

class DocumentationChecker:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.features_file = self.docs_dir / "features.md"
        self.last_check_file = self.docs_dir / ".last_check"
        self._load_last_check()

    def _load_last_check(self) -> None:
        """前回のチェック情報を読み込む"""
        try:
            if self.last_check_file.exists():
                with open(self.last_check_file, 'r', encoding='utf-8') as f:
                    self.last_check = json.load(f)
            else:
                self.last_check = {
                    "last_check_time": datetime.now().isoformat(),
                    "implementation_status": {},
                    "documentation_status": {}
                }
        except json.JSONDecodeError as e:
            raise DocumentError(
                f"前回のチェック情報ファイル（{self.last_check_file}）の読み込みに失敗しました。"
                f"ファイルが破損している可能性があります。エラー詳細: {str(e)}"
            )
        except Exception as e:
            raise DocumentError(
                f"チェック情報の読み込み中に予期せぬエラーが発生しました。"
                f"エラー詳細: {str(e)}"
            )

    def _save_last_check(self) -> None:
        """チェック情報を保存"""
        try:
            self.last_check["last_check_time"] = datetime.now().isoformat()
            with open(self.last_check_file, 'w', encoding='utf-8') as f:
                json.dump(self.last_check, f, indent=2)
        except Exception as e:
            raise DocumentError(
                f"チェック情報の保存に失敗しました。"
                f"ファイル: {self.last_check_file}, エラー詳細: {str(e)}"
            )

    def check_implementation_status(self) -> Dict[str, Any]:
        """実装状況のチェック"""
        if not self.features_file.exists():
            raise DocumentError(
                f"機能仕様書が見つかりません。"
                f"期待される場所: {self.features_file}"
            )

        try:
            with open(self.features_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise DocumentError(
                f"機能仕様書の読み込みに失敗しました。"
                f"ファイル: {self.features_file}, エラー詳細: {str(e)}"
            )

        # 実装状況のマーカーを検索
        implemented = len(re.findall(r'✅', content))
        in_progress = len(re.findall(r'🔄', content))
        not_implemented = len(re.findall(r'❌', content))
        total = implemented + in_progress + not_implemented

        if total == 0:
            raise DocumentError(
                f"機能仕様書に実装状況のマーカー（✅、🔄、❌）が見つかりません。"
                f"ファイル: {self.features_file}"
            )

        return {
            "implemented": implemented,
            "in_progress": in_progress,
            "not_implemented": not_implemented,
            "total": total,
            "implementation_rate": (implemented / total * 100) if total > 0 else 0
        }

    def check_documentation_updates(self) -> List[str]:
        """ドキュメント更新のチェック"""
        updates_needed = []
        
        try:
            # 機能仕様書の最終更新日時を確認
            features_mtime = datetime.fromtimestamp(self.features_file.stat().st_mtime)
            last_check_time = datetime.fromisoformat(self.last_check["last_check_time"])
            
            if features_mtime < last_check_time:
                updates_needed.append(
                    f"機能仕様書の更新が必要です。"
                    f"最終更新: {features_mtime.isoformat()}, "
                    f"前回チェック: {last_check_time.isoformat()}"
                )

            # 実装状況の変更を確認
            current_status = self.check_implementation_status()
            if current_status != self.last_check.get("implementation_status"):
                updates_needed.append(
                    f"実装状況の更新が必要です。"
                    f"変更前: {self.last_check.get('implementation_status')}, "
                    f"変更後: {current_status}"
                )

            return updates_needed
        except Exception as e:
            raise DocumentError(
                f"ドキュメント更新のチェック中にエラーが発生しました。"
                f"エラー詳細: {str(e)}"
            )

    def run_check(self) -> Dict[str, Any]:
        """チェックを実行"""
        try:
            implementation_status = self.check_implementation_status()
            documentation_updates = self.check_documentation_updates()
            
            self.last_check["implementation_status"] = implementation_status
            self._save_last_check()

            return {
                "status": "success",
                "implementation_status": implementation_status,
                "documentation_updates_needed": documentation_updates,
                "check_time": datetime.now().isoformat()
            }
        except Exception as e:
            error_message = (
                f"ドキュメントチェック中にエラーが発生しました。\n"
                f"エラーの種類: {type(e).__name__}\n"
                f"エラー詳細: {str(e)}\n"
                f"チェック対象ファイル: {self.features_file}"
            )
            logger.error(error_message)
            return {
                "status": "error",
                "error": error_message,
                "check_time": datetime.now().isoformat()
            }

    def generate_report(self) -> str:
        """チェック結果のレポートを生成"""
        result = self.run_check()
        
        if result["status"] == "error":
            return (
                "ドキュメントチェックでエラーが発生しました\n"
                "----------------------------------------\n"
                f"{result['error']}\n"
                "----------------------------------------\n"
                "このエラーを解決するには、上記のエラーメッセージを確認し、"
                "必要な対応を行ってください。"
            )

        report = [
            "ドキュメントチェックレポート",
            "----------------------------------------",
            f"チェック実行日時: {result['check_time']}",
            "\n実装状況:",
            f"- 実装済み: {result['implementation_status']['implemented']}",
            f"- 開発中: {result['implementation_status']['in_progress']}",
            f"- 未実装: {result['implementation_status']['not_implemented']}",
            f"- 実装率: {result['implementation_status']['implementation_rate']:.1f}%",
            "\n必要な更新:"
        ]

        if result["documentation_updates_needed"]:
            for update in result["documentation_updates_needed"]:
                report.append(f"- {update}")
        else:
            report.append("- 更新は必要ありません")

        report.append("----------------------------------------")
        return "\n".join(report) 