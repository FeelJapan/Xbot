"""
動画生成サービスのテスト
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import os

from app.services.video_generator import VideoGenerator
from core.error_handling.error_handler import VideoGenerationError

@pytest.fixture
def video_generator():
    """テスト用の動画生成器"""
    return VideoGenerator(api_key="test_api_key")

@pytest.fixture
def mock_response():
    """モックレスポンス"""
    mock = Mock()
    mock.status = 200
    mock.json = AsyncMock(return_value={
        "candidates": [{
            "content": {
                "parts": [{
                    "text": "Generated video content"
                }]
            }
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

class TestVideoGenerator:
    """動画生成器のテストクラス"""
    
    def test_init_with_api_key(self):
        """APIキー付きでの初期化テスト"""
        generator = VideoGenerator(api_key="test_key")
        assert generator.api_key == "test_key"
        assert generator.base_url == "https://generativelanguage.googleapis.com/v1beta/models"
        assert generator.model == "gemini-1.5-flash"
        assert generator.default_params["duration"] == 5
    
    def test_init_without_api_key(self):
        """APIキーなしでの初期化テスト"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env_key"}):
            generator = VideoGenerator()
            assert generator.api_key == "env_key"
    
    def test_init_without_api_key_no_env(self):
        """APIキーなし・環境変数なしでの初期化テスト"""
        with patch.dict(os.environ, {}, clear=True):
            generator = VideoGenerator()
            assert generator.api_key is None
    
    @pytest.mark.asyncio
    async def test_generate_video_success(self, video_generator, mock_response):
        """動画生成成功のテスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await video_generator.generate_video("test prompt")
            
            assert result["candidates"][0]["content"]["parts"][0]["text"] == "Generated video content"
    
    @pytest.mark.asyncio
    async def test_generate_video_no_api_key(self):
        """APIキーなしでの動画生成テスト"""
        generator = VideoGenerator(api_key=None)
        
        with pytest.raises(VideoGenerationError, match="Gemini APIキーが設定されていません"):
            await generator.generate_video("test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_video_api_error(self, video_generator, mock_error_response):
        """APIエラー時の動画生成テスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_error_response
            
            with pytest.raises(VideoGenerationError, match="動画生成に失敗しました"):
                await video_generator.generate_video("test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_video_with_custom_params(self, video_generator, mock_response):
        """カスタムパラメータでの動画生成テスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await video_generator.generate_video(
                "test prompt",
                duration=10,
                resolution="4K",
                fps=60
            )
            
            assert result["candidates"][0]["content"]["parts"][0]["text"] == "Generated video content"
    
    def test_create_video_prompt_cinematic(self, video_generator):
        """シネマティックスタイルのプロンプト作成テスト"""
        result = video_generator.create_video_prompt("cat", "cinematic")
        assert "cat" in result
        assert "cinematic" in result
        assert "professional camera work" in result
        assert "high quality video" in result
    
    def test_create_video_prompt_vlog(self, video_generator):
        """Vlogスタイルのプロンプト作成テスト"""
        result = video_generator.create_video_prompt("cat", "vlog")
        assert "cat" in result
        assert "vlog style" in result
        assert "handheld camera" in result
    
    def test_create_video_prompt_unknown_style(self, video_generator):
        """未知のスタイルでのプロンプト作成テスト"""
        result = video_generator.create_video_prompt("cat", "unknown")
        assert "cat" in result
        assert "cinematic" in result  # デフォルトスタイルが使用される
    
    def test_create_video_prompt_default_style(self, video_generator):
        """デフォルトスタイルでのプロンプト作成テスト"""
        result = video_generator.create_video_prompt("cat")
        assert "cat" in result
        assert "cinematic" in result
    
    def test_adjust_video_parameters_normal(self, video_generator):
        """正常なパラメータ調整テスト"""
        result = video_generator.adjust_video_parameters(10, "1080p", 30)
        assert result["duration"] == 10
        assert result["resolution"] == "1080p"
        assert result["fps"] == 30
    
    def test_adjust_video_parameters_duration_too_short(self, video_generator):
        """短すぎる動画時間の調整テスト"""
        result = video_generator.adjust_video_parameters(0, "1080p", 30)
        assert result["duration"] == 1
    
    def test_adjust_video_parameters_duration_too_long(self, video_generator):
        """長すぎる動画時間の調整テスト"""
        result = video_generator.adjust_video_parameters(100, "1080p", 30)
        assert result["duration"] == 60
    
    def test_adjust_video_parameters_fps_too_low(self, video_generator):
        """低すぎるフレームレートの調整テスト"""
        result = video_generator.adjust_video_parameters(10, "1080p", 20)
        assert result["fps"] == 24
    
    def test_adjust_video_parameters_fps_too_high(self, video_generator):
        """高すぎるフレームレートの調整テスト"""
        result = video_generator.adjust_video_parameters(10, "1080p", 100)
        assert result["fps"] == 60
    
    def test_adjust_video_parameters_invalid_resolution(self, video_generator):
        """無効な解像度の調整テスト"""
        result = video_generator.adjust_video_parameters(10, "invalid", 30)
        assert result["resolution"] == "1080p"
    
    @pytest.mark.asyncio
    async def test_edit_video_success(self, video_generator):
        """動画編集成功のテスト"""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file.write(b"fake video data")
            temp_file_path = temp_file.name
        
        try:
            result = await video_generator.edit_video(temp_file_path, "Add text overlay")
            assert result["status"] == "success"
            assert "動画編集が完了しました" in result["message"]
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_edit_video_file_not_found(self, video_generator):
        """存在しないファイルでの動画編集テスト"""
        with pytest.raises(VideoGenerationError, match="動画ファイルが見つかりません"):
            await video_generator.edit_video("nonexistent.mp4", "Add text overlay")
    
    @pytest.mark.asyncio
    async def test_trim_video_success(self, video_generator):
        """動画トリミング成功のテスト"""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file.write(b"fake video data")
            temp_file_path = temp_file.name
        
        try:
            result = await video_generator.trim_video(temp_file_path, 1.0, 5.0)
            assert result.endswith("_trimmed.mp4")
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_trim_video_file_not_found(self, video_generator):
        """存在しないファイルでの動画トリミングテスト"""
        with pytest.raises(VideoGenerationError, match="動画ファイルが見つかりません"):
            await video_generator.trim_video("nonexistent.mp4", 1.0, 5.0)
    
    @pytest.mark.asyncio
    async def test_save_generated_video_success(self, video_generator):
        """動画保存成功のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            video_data = b"fake video data"
            result = await video_generator.save_generated_video(video_data, save_dir=temp_dir)
            
            assert Path(result).exists()
            assert Path(result).suffix == ".mp4"
            assert "generated_video_" in Path(result).name
            
            # 保存されたデータを確認
            with open(result, "rb") as f:
                saved_data = f.read()
            assert saved_data == video_data
    
    def test_get_generation_history(self, video_generator):
        """生成履歴取得テスト"""
        history = video_generator.get_generation_history()
        assert isinstance(history, list)
        assert len(history) == 0  # 現在は空のリストを返す
    
    def test_clear_history(self, video_generator):
        """履歴クリアテスト"""
        result = video_generator.clear_history()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_generate_video_network_error(self, video_generator):
        """ネットワークエラー時のテスト"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.side_effect = Exception("Network error")
            
            with pytest.raises(VideoGenerationError, match="動画生成中にエラーが発生しました"):
                await video_generator.generate_video("test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_video_json_error(self, video_generator):
        """JSON解析エラー時のテスト"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=Exception("JSON error"))
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(VideoGenerationError, match="動画生成中にエラーが発生しました"):
                await video_generator.generate_video("test prompt")
    
    def test_create_video_prompt_empty_base(self, video_generator):
        """空のベースプロンプトでのテスト"""
        result = video_generator.create_video_prompt("", "cinematic")
        assert "cinematic" in result
        assert "high quality video" in result
    
    def test_create_video_prompt_all_styles(self, video_generator):
        """全スタイルでのプロンプト作成テスト"""
        styles = ["cinematic", "vlog", "commercial", "documentary", "animation"]
        
        for style in styles:
            result = video_generator.create_video_prompt("test", style)
            assert "test" in result
            assert "high quality video" in result 