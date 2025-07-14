"""
ドキュメントチェックのコマンドラインツール
"""
import argparse
from pathlib import Path
from .checker import DocumentationChecker
from ..logging.logger import get_logger

logger = get_logger("documentation_cli")

def main():
    parser = argparse.ArgumentParser(description="ドキュメントチェックツール")
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="docs",
        help="ドキュメントディレクトリのパス"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="レポートの出力先ファイル（指定がない場合は標準出力）"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="出力フォーマット"
    )

    args = parser.parse_args()

    try:
        checker = DocumentationChecker(docs_dir=args.docs_dir)
        result = checker.run_check()

        if args.format == "json":
            output = result
        else:
            output = checker.generate_report()

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                if args.format == "json":
                    import json
                    json.dump(output, f, indent=2, ensure_ascii=False)
                else:
                    f.write(output)
        else:
            if args.format == "json":
                import json
                print(json.dumps(output, indent=2, ensure_ascii=False))
            else:
                print(output)

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main()) 