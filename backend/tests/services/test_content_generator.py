"""
コンテンツ生成サービスのテスト
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import json
import sqlite3

from backend.app.services.content_generator import (
    ContentGenerator,
    GenerationRequest,
    GenerationResult,
    PromptTemplate
)
from backend.core.error_handling.error_handler import ContentGenerationError

@pytest.fixture
def temp_db():
    """一時データベース"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    os.unlink(db_path)

@pytest.fixture
def content_generator(temp_db):
    """コンテンツ生成器"""
    return ContentGenerator(api_key="test_key", db_path=temp_db)

@pytest.fixture
def mock_response():
    """モックレスポンス"""
    mock = Mock()
    mock.status = 200
    mock.json = AsyncMock(return_value={
        "choices": [{
            "message": {
                "content": "Generated test content"
            }
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    })
    return mock

@pytest.fixture
def sample_template():
    """サンプルテンプレート"""
    return PromptTemplate(
        name="test_template",
        template="Template: {prompt}",
        description="Test template",
        category="test",
        parameters={"temperature": 0.7},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

class TestContentGenerator:
    """コンテンツ生成器のテスト"""
    
    def test_init(self, temp_db):
        """初期化テスト"""
        generator = ContentGenerator(api_key="test_key", db_path=temp_db)
        assert generator.api_key == "test_key"
        assert generator.db_path == temp_db
        assert generator.base_url == "https://api.openai.com/v1/chat/completions"
    
    def test_init_with_env_var(self, temp_db, monkeypatch):
        """環境変数での初期化テスト"""
        monkeypatch.setenv("OPENAI_API_KEY", "env_key")
        generator = ContentGenerator(db_path=temp_db)
        assert generator.api_key == "env_key"
    
    def test_database_initialization(self, temp_db):
        """データベース初期化テスト"""
        generator = ContentGenerator(api_key="test_key", db_path=temp_db)
        
        # データベースファイルが作成されていることを確認
        assert os.path.exists(temp_db)
        
        # テーブルが作成されていることを確認
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert "generation_history" in tables
            assert "prompt_templates" in tables
    
    @pytest.mark.asyncio
    async def test_generate_text_success(self, content_generator, mock_response):
        """テキスト生成成功のテスト"""
        request = GenerationRequest(
            prompt="Test prompt",
            temperature=0.7,
            max_tokens=100
        )
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await content_generator.generate_text(request)
            
            assert isinstance(result, GenerationResult)
            assert result.content == "Generated test content"
            assert result.prompt == "Test prompt"
            assert result.template_name is None
            assert result.model == "gpt-3.5-turbo"
            assert result.usage is not None
            assert result.usage["total_tokens"] == 30
    
    @pytest.mark.asyncio
    async def test_generate_text_no_api_key(self, content_generator):
        """APIキーなしでのテキスト生成テスト"""
        request = GenerationRequest(prompt="Test prompt")
        content_generator.api_key = None
        
        with pytest.raises(ContentGenerationError, match="OpenAI APIキーが設定されていません"):
            await content_generator.generate_text(request)
    
    @pytest.mark.asyncio
    async def test_generate_text_api_error(self, content_generator):
        """APIエラー時のテキスト生成テスト"""
        request = GenerationRequest(prompt="Test prompt")
        
        mock_response = Mock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="API Error")
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ContentGenerationError, match="テキスト生成に失敗しました"):
                await content_generator.generate_text(request)
    
    @pytest.mark.asyncio
    async def test_generate_text_with_template(self, content_generator, mock_response, sample_template):
        """テンプレート付きテキスト生成テスト"""
        # テンプレートを追加
        content_generator.add_prompt_template(sample_template)
        
        request = GenerationRequest(
            prompt="Test prompt",
            template_name="test_template"
        )
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await content_generator.generate_text(request)
            
            assert result.prompt == "Template: Test prompt"
    
    @pytest.mark.asyncio
    async def test_generate_variations(self, content_generator, mock_response):
        """複数バリエーション生成テスト"""
        request = GenerationRequest(
            prompt="Test prompt",
            temperature=0.7
        )
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            variations = await content_generator.generate_variations(request, count=3)
            
            assert len(variations) == 3
            for i, variation in enumerate(variations):
                assert isinstance(variation, GenerationResult)
                assert variation.content == "Generated test content"
                # 温度パラメータが少しずつ異なることを確認
                expected_temp = 0.7 + (i * 0.1)
                assert variation.parameters["temperature"] == expected_temp
    
    def test_add_prompt_template(self, content_generator, sample_template):
        """プロンプトテンプレート追加テスト"""
        content_generator.add_prompt_template(sample_template)
        
        templates = content_generator.get_prompt_templates()
        assert len(templates) == 1
        assert templates[0].name == "test_template"
        assert templates[0].template == "Template: {prompt}"
    
    def test_get_prompt_templates_by_category(self, content_generator, sample_template):
        """カテゴリ別テンプレート取得テスト"""
        content_generator.add_prompt_template(sample_template)
        
        # 正しいカテゴリで検索
        templates = content_generator.get_prompt_templates(category="test")
        assert len(templates) == 1
        assert templates[0].name == "test_template"
        
        # 存在しないカテゴリで検索
        templates = content_generator.get_prompt_templates(category="nonexistent")
        assert len(templates) == 0
    
    def test_get_generation_history(self, content_generator):
        """生成履歴取得テスト"""
        history = content_generator.get_generation_history()
        assert isinstance(history, list)
        assert len(history) == 0  # 初期状態では空
    
    def test_get_generation_history_with_limit(self, content_generator):
        """制限付き生成履歴取得テスト"""
        history = content_generator.get_generation_history(limit=10, offset=5)
        assert isinstance(history, list)
    
    def test_clear_history(self, content_generator):
        """履歴クリアテスト"""
        deleted_count = content_generator.clear_history()
        assert deleted_count == 0  # 初期状態では削除する履歴がない
    
    def test_clear_history_before_date(self, content_generator):
        """日付指定履歴クリアテスト"""
        before_date = datetime.now()
        deleted_count = content_generator.clear_history(before_date=before_date)
        assert deleted_count == 0
    
    def test_get_statistics(self, content_generator):
        """統計取得テスト"""
        stats = content_generator.get_statistics()
        
        assert "total_generations" in stats
        assert "today_generations" in stats
        assert "template_stats" in stats
        assert "average_content_length" in stats
        
        assert stats["total_generations"] == 0
        assert stats["today_generations"] == 0
        assert isinstance(stats["template_stats"], dict)
        assert stats["average_content_length"] == 0.0
    
    def test_apply_template_not_found(self, content_generator):
        """存在しないテンプレート適用テスト"""
        request = GenerationRequest(
            prompt="Test prompt",
            template_name="nonexistent_template"
        )
        
        final_prompt = content_generator._apply_template(request)
        assert final_prompt == "Test prompt"  # 元のプロンプトが返される
    
    def test_get_system_prompt(self, content_generator):
        """システムプロンプト取得テスト"""
        # カジュアルスタイル
        prompt = content_generator._get_system_prompt("casual", "日本語")
        assert "親しみやすく、カジュアルな口調で" in prompt
        assert "日本語" in prompt
        
        # フォーマルスタイル
        prompt = content_generator._get_system_prompt("formal", "英語")
        assert "丁寧で、フォーマルな口調で" in prompt
        assert "英語" in prompt
        
        # 存在しないスタイル
        prompt = content_generator._get_system_prompt("unknown", "日本語")
        assert "親しみやすく、カジュアルな口調で" in prompt  # デフォルトスタイル
    
    def test_create_variation_request(self, content_generator):
        """バリエーションリクエスト作成テスト"""
        base_request = GenerationRequest(
            prompt="Test prompt",
            temperature=0.5,
            max_tokens=100
        )
        
        variation = content_generator._create_variation_request(base_request, 1)
        
        assert variation.prompt == "Test prompt"
        assert variation.temperature == 0.6  # 0.5 + 0.1
        assert variation.max_tokens == 100
    
    def test_generate_id(self, content_generator):
        """ID生成テスト"""
        id1 = content_generator._generate_id()
        id2 = content_generator._generate_id()
        
        assert id1 != id2
        assert id1.startswith("gen_")
        assert id2.startswith("gen_")
    
    @pytest.mark.asyncio
    async def test_save_to_history(self, content_generator):
        """履歴保存テスト"""
        result = GenerationResult(
            id="test_id",
            content="Test content",
            prompt="Test prompt",
            template_name=None,
            parameters={"temperature": 0.7},
            created_at=datetime.now(),
            model="gpt-3.5-turbo",
            usage={"total_tokens": 30}
        )
        
        await content_generator._save_to_history(result)
        
        # 履歴に保存されていることを確認
        history = content_generator.get_generation_history()
        assert len(history) == 1
        assert history[0].id == "test_id"
        assert history[0].content == "Test content"
    
    @pytest.mark.asyncio
    async def test_generate_text_network_error(self, content_generator):
        """ネットワークエラー時のテスト"""
        request = GenerationRequest(prompt="Test prompt")
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.side_effect = Exception("Network error")
            
            with pytest.raises(ContentGenerationError, match="テキスト生成中にエラーが発生しました"):
                await content_generator.generate_text(request)
    
    def test_template_parameters(self, content_generator):
        """テンプレートパラメータテスト"""
        template = PromptTemplate(
            name="parameter_test",
            template="Temperature: {temperature}, Tokens: {max_tokens}",
            description="Parameter test",
            category="test",
            parameters={"temperature": 0.8, "max_tokens": 500},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        content_generator.add_prompt_template(template)
        
        templates = content_generator.get_prompt_templates()
        assert len(templates) == 1
        assert templates[0].parameters["temperature"] == 0.8
        assert templates[0].parameters["max_tokens"] == 500 