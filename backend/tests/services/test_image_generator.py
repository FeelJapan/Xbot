"""
画像生成サービスのテスト
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import os

from app.services.image_generator import ImageGenerator
from core.error_handling.error_handler import ImageGenerationError

@pytest.fixture
def image_generator():
    """テスト用の画像生成器"""
    return ImageGenerator(api_key="test_api_key")

@pytest.fixture
def mock_response():
    """モックレスポンス"""
    mock = Mock()
    mock.status = 200
    mock.json = AsyncMock(return_value={
        "data": [{
            "url": "https://example.com/generated_image.png",
            "revised_prompt": "test prompt"
        }]
    })
    return mock

@pytest.fixture
def mock_error_response():
    """エラーレスポンスのモック"""
    mock = Mock()
    mock.status = 400
    mock.text = AsyncMock(return_value="Bad Request")
    return mock

class TestImageGenerator:
    """画像生成器のテストクラス"""
    
    def test_init_with_api_key(self):
        """APIキー付きでの初期化テスト"""
        generator = ImageGenerator(api_key="test_key")
        assert generator.api_key == "test_key"
        assert generator.base_url == "https://api.openai.com/v1/images"
        assert generator.default_params["model"] == "dall-e-3"
    
    def test_init_without_api_key(self):
        """APIキーなしでの初期化テスト"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env_key"}):
            generator = ImageGenerator()
            assert generator.api_key == "env_key"
    
    def test_init_without_api_key_no_env(self):
        """APIキーなし・環境変数なしでの初期化テスト"""
        with patch.dict(os.environ, {}, clear=True):
            generator = ImageGenerator()
            assert generator.api_key is None
    
    @pytest.mark.asyncio
    async def test_generate_image_success(self, image_generator, mock_response):
        """画像生成成功のテスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await image_generator.generate_image("test prompt")
            
            assert result["data"][0]["url"] == "https://example.com/generated_image.png"
            assert result["data"][0]["revised_prompt"] == "test prompt"
    
    @pytest.mark.asyncio
    async def test_generate_image_no_api_key(self):
        """APIキーなしでの画像生成テスト"""
        generator = ImageGenerator(api_key=None)
        
        with pytest.raises(ImageGenerationError, match="OpenAI APIキーが設定されていません"):
            await generator.generate_image("test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_image_api_error(self, image_generator, mock_error_response):
        """APIエラー時の画像生成テスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_error_response
            
            with pytest.raises(ImageGenerationError, match="画像生成に失敗しました"):
                await image_generator.generate_image("test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_image_with_custom_params(self, image_generator, mock_response):
        """カスタムパラメータでの画像生成テスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await image_generator.generate_image(
                "test prompt",
                size="512x512",
                quality="hd",
                style="natural"
            )
            
            assert result["data"][0]["url"] == "https://example.com/generated_image.png"
    
    @pytest.mark.asyncio
    async def test_generate_variations_success(self, image_generator, mock_response):
        """画像バリエーション生成成功のテスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_file.write(b"fake image data")
                temp_file_path = temp_file.name
            
            try:
                result = await image_generator.generate_variations(temp_file_path, n=2)
                assert result["data"][0]["url"] == "https://example.com/generated_image.png"
            finally:
                os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_generate_variations_no_api_key(self):
        """APIキーなしでのバリエーション生成テスト"""
        generator = ImageGenerator(api_key=None)
        
        with pytest.raises(ImageGenerationError, match="OpenAI APIキーが設定されていません"):
            await generator.generate_variations("nonexistent.png")
    
    @pytest.mark.asyncio
    async def test_generate_variations_file_not_found(self, image_generator):
        """存在しないファイルでのバリエーション生成テスト"""
        with pytest.raises(ImageGenerationError, match="元画像が見つかりません"):
            await image_generator.generate_variations("nonexistent.png")
    
    def test_optimize_prompt_basic(self, image_generator):
        """基本的なプロンプト最適化テスト"""
        result = image_generator.optimize_prompt("cat")
        assert "high quality photo of cat" in result
        assert "high resolution" in result
        assert "professional photography" in result
    
    def test_optimize_prompt_with_photo_keyword(self, image_generator):
        """写真キーワード付きプロンプトの最適化テスト"""
        result = image_generator.optimize_prompt("photo of a cat")
        assert "high quality photo of photo of a cat" in result
    
    def test_optimize_prompt_empty(self, image_generator):
        """空のプロンプト最適化テスト"""
        result = image_generator.optimize_prompt("")
        assert "high quality photo of" in result
    
    def test_optimize_prompt_whitespace(self, image_generator):
        """空白付きプロンプト最適化テスト"""
        result = image_generator.optimize_prompt("  cat  ")
        assert "high quality photo of cat" in result
    
    @pytest.mark.asyncio
    async def test_save_generated_image_success(self, image_generator):
        """画像保存成功のテスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.read = AsyncMock(return_value=b"fake image data")
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            with tempfile.TemporaryDirectory() as temp_dir:
                result = await image_generator.save_generated_image(
                    "https://example.com/image.png",
                    save_dir=temp_dir
                )
                
                assert Path(result).exists()
                assert Path(result).suffix == ".png"
                assert "generated_image_" in Path(result).name
    
    @pytest.mark.asyncio
    async def test_save_generated_image_download_error(self, image_generator):
        """画像ダウンロードエラー時のテスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = Mock()
            mock_response.status = 404
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ImageGenerationError, match="画像のダウンロードに失敗しました"):
                await image_generator.save_generated_image("https://example.com/image.png")
    
    def test_get_generation_history(self, image_generator):
        """生成履歴取得テスト"""
        history = image_generator.get_generation_history()
        assert isinstance(history, list)
        assert len(history) == 0  # 現在は空のリストを返す
    
    def test_clear_history(self, image_generator):
        """履歴クリアテスト"""
        result = image_generator.clear_history()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_generate_image_network_error(self, image_generator):
        """ネットワークエラー時のテスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.side_effect = Exception("Network error")
            
            with pytest.raises(ImageGenerationError, match="画像生成中にエラーが発生しました"):
                await image_generator.generate_image("test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_image_json_error(self, image_generator):
        """JSON解析エラー時のテスト"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=Exception("JSON error"))
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ImageGenerationError, match="画像生成中にエラーが発生しました"):
                await image_generator.generate_image("test prompt") 