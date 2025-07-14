"""
投稿管理APIエンドポイント
投稿の作成、編集、スケジュール、実行などの機能を提供
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from app.services.post_manager import PostManager, Post, PostContent, PostType, PostStatus, PostTemplate
from app.services.scheduler import PostScheduler, PostSchedule, ScheduleType
from core.logging.logger import get_logger

logger = get_logger("post_management_api")

router = APIRouter()

# サービスインスタンス
post_manager = PostManager()
scheduler = PostScheduler()

# リクエストモデル
class PostContentRequest(BaseModel):
    text: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    links: Optional[List[str]] = None

class CreatePostRequest(BaseModel):
    content: PostContentRequest
    post_type: str = "text"  # "text", "image", "video", "mixed"
    template_name: Optional[str] = None
    scheduled_time: Optional[datetime] = None

class UpdatePostRequest(BaseModel):
    content: Optional[PostContentRequest] = None
    scheduled_time: Optional[datetime] = None

class SchedulePostRequest(BaseModel):
    scheduled_time: datetime
    schedule_type: str = "once"  # "once", "daily", "weekly", "monthly"

class CreateRecurringScheduleRequest(BaseModel):
    post_template: str
    start_time: datetime
    end_time: Optional[datetime] = None
    schedule_type: str = "daily"
    interval_hours: int = 24
    days_of_week: Optional[List[int]] = None
    max_posts_per_day: int = 3

class PostTemplateRequest(BaseModel):
    name: str
    content_template: str
    post_type: str = "text"
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    tone: Optional[str] = "professional"
    max_length: Optional[int] = 280
    include_link: bool = False
    include_media: bool = False

class UpdatePostTemplateRequest(BaseModel):
    content_template: Optional[str] = None
    post_type: Optional[str] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    tone: Optional[str] = None
    max_length: Optional[int] = None
    include_link: Optional[bool] = None
    include_media: Optional[bool] = None

# レスポンスモデル
class PostResponse(BaseModel):
    id: str
    content: Dict[str, Any]
    scheduled_time: Optional[datetime]
    status: str
    post_type: str
    template_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    posted_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: str
    post_id: str
    scheduled_time: datetime
    schedule_type: str
    status: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class PostTemplateResponse(BaseModel):
    name: str
    content_template: str
    post_type: str
    hashtags: List[str]
    mentions: List[str]
    tone: str
    max_length: int
    include_link: bool
    include_media: bool

class StatisticsResponse(BaseModel):
    total_schedules: int
    pending_schedules: int
    executed_schedules: int
    failed_schedules: int
    cancelled_schedules: int
    today_schedules: int
    success_rate: float

@router.post("/posts", response_model=PostResponse)
async def create_post(request: CreatePostRequest):
    """投稿を作成"""
    try:
        # PostContentオブジェクトを作成
        content = PostContent(
            text=request.content.text,
            image_url=request.content.image_url,
            video_url=request.content.video_url,
            hashtags=request.content.hashtags or [],
            mentions=request.content.mentions or [],
            links=request.content.links or []
        )
        
        # PostTypeを変換
        post_type = PostType(request.post_type)
        
        # 投稿を作成
        post = post_manager.create_post(
            content=content,
            post_type=post_type,
            template_name=request.template_name,
            scheduled_time=request.scheduled_time
        )
        
        # スケジュール時間が指定されている場合はスケジュール
        if request.scheduled_time:
            scheduler.schedule_post(
                post_id=post.id,
                scheduled_time=request.scheduled_time,
                schedule_type=ScheduleType.ONCE
            )
        
        logger.info(f"投稿を作成しました: {post.id}")
        return PostResponse(
            id=post.id,
            content={
                "text": post.content.text,
                "image_url": post.content.image_url,
                "video_url": post.content.video_url,
                "hashtags": post.content.hashtags,
                "mentions": post.content.mentions,
                "links": post.content.links
            },
            scheduled_time=post.scheduled_time,
            status=post.status.value,
            post_type=post.post_type.value,
            template_name=post.template_name,
            created_at=post.created_at,
            updated_at=post.updated_at,
            posted_at=post.posted_at,
            error_message=post.error_message
        )
        
    except Exception as e:
        logger.error(f"投稿の作成に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    status: Optional[str] = None,
    post_type: Optional[str] = None,
    limit: int = 50
):
    """投稿一覧を取得"""
    try:
        # ステータスとタイプを変換
        post_status = PostStatus(status) if status else None
        post_type_enum = PostType(post_type) if post_type else None
        
        posts = post_manager.get_posts(
            status=post_status,
            post_type=post_type_enum,
            limit=limit
        )
        
        return [
            PostResponse(
                id=post.id,
                content={
                    "text": post.content.text,
                    "image_url": post.content.image_url,
                    "video_url": post.content.video_url,
                    "hashtags": post.content.hashtags,
                    "mentions": post.content.mentions,
                    "links": post.content.links
                },
                scheduled_time=post.scheduled_time,
                status=post.status.value,
                post_type=post.post_type.value,
                template_name=post.template_name,
                created_at=post.created_at,
                updated_at=post.updated_at,
                posted_at=post.posted_at,
                error_message=post.error_message
            )
            for post in posts
        ]
        
    except Exception as e:
        logger.error(f"投稿一覧の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    """投稿を取得"""
    try:
        post = post_manager.get_post(post_id)
        if post is None:
            raise HTTPException(status_code=404, detail="投稿が見つかりません")
        
        return PostResponse(
            id=post.id,
            content={
                "text": post.content.text,
                "image_url": post.content.image_url,
                "video_url": post.content.video_url,
                "hashtags": post.content.hashtags,
                "mentions": post.content.mentions,
                "links": post.content.links
            },
            scheduled_time=post.scheduled_time,
            status=post.status.value,
            post_type=post.post_type.value,
            template_name=post.template_name,
            created_at=post.created_at,
            updated_at=post.updated_at,
            posted_at=post.posted_at,
            error_message=post.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"投稿の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, request: UpdatePostRequest):
    """投稿を更新"""
    try:
        # 更新データを準備
        update_data = {}
        
        if request.content:
            content = PostContent(
                text=request.content.text,
                image_url=request.content.image_url,
                video_url=request.content.video_url,
                hashtags=request.content.hashtags or [],
                mentions=request.content.mentions or [],
                links=request.content.links or []
            )
            update_data["content"] = content
        
        if request.scheduled_time:
            update_data["scheduled_time"] = request.scheduled_time
        
        # 投稿を更新
        post = post_manager.update_post(post_id, **update_data)
        
        logger.info(f"投稿を更新しました: {post_id}")
        return PostResponse(
            id=post.id,
            content={
                "text": post.content.text,
                "image_url": post.content.image_url,
                "video_url": post.content.video_url,
                "hashtags": post.content.hashtags,
                "mentions": post.content.mentions,
                "links": post.content.links
            },
            scheduled_time=post.scheduled_time,
            status=post.status.value,
            post_type=post.post_type.value,
            template_name=post.template_name,
            created_at=post.created_at,
            updated_at=post.updated_at,
            posted_at=post.posted_at,
            error_message=post.error_message
        )
        
    except Exception as e:
        logger.error(f"投稿の更新に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    """投稿を削除"""
    try:
        success = post_manager.delete_post(post_id)
        if not success:
            raise HTTPException(status_code=404, detail="投稿が見つかりません")
        
        logger.info(f"投稿を削除しました: {post_id}")
        return {"message": "投稿を削除しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"投稿の削除に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/schedule", response_model=ScheduleResponse)
async def schedule_post(post_id: str, request: SchedulePostRequest):
    """投稿をスケジュール"""
    try:
        # スケジュールタイプを変換
        schedule_type = ScheduleType(request.schedule_type)
        
        # スケジュールを作成
        schedule = scheduler.schedule_post(
            post_id=post_id,
            scheduled_time=request.scheduled_time,
            schedule_type=schedule_type
        )
        
        logger.info(f"投稿をスケジュールしました: {schedule.id}")
        return ScheduleResponse(
            id=schedule.id,
            post_id=schedule.post_id,
            scheduled_time=schedule.scheduled_time,
            schedule_type=schedule.schedule_type.value,
            status=schedule.status,
            created_at=schedule.created_at,
            executed_at=schedule.executed_at,
            error_message=schedule.error_message
        )
        
    except Exception as e:
        logger.error(f"投稿のスケジュールに失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/post-now")
async def post_now(post_id: str, background_tasks: BackgroundTasks):
    """投稿を即座に実行"""
    try:
        # バックグラウンドで投稿を実行
        background_tasks.add_task(post_manager.post_now, post_id)
        
        logger.info(f"投稿の即座実行を開始しました: {post_id}")
        return {"message": "投稿の実行を開始しました"}
        
    except Exception as e:
        logger.error(f"投稿の即座実行に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}/preview")
async def preview_post(post_id: str):
    """投稿のプレビューを取得"""
    try:
        preview = post_manager.preview_post(post_id)
        return preview
        
    except Exception as e:
        logger.error(f"投稿プレビューの取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drafts", response_model=List[PostResponse])
async def get_drafts():
    """下書き一覧を取得"""
    try:
        drafts = post_manager.get_drafts()
        
        return [
            PostResponse(
                id=draft.id,
                content={
                    "text": draft.content.text,
                    "image_url": draft.content.image_url,
                    "video_url": draft.content.video_url,
                    "hashtags": draft.content.hashtags,
                    "mentions": draft.content.mentions,
                    "links": draft.content.links
                },
                scheduled_time=draft.scheduled_time,
                status=draft.status.value,
                post_type=draft.post_type.value,
                template_name=draft.template_name,
                created_at=draft.created_at,
                updated_at=draft.updated_at,
                posted_at=draft.posted_at,
                error_message=draft.error_message
            )
            for draft in drafts
        ]
        
    except Exception as e:
        logger.error(f"下書き一覧の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedules", response_model=List[ScheduleResponse])
async def get_schedules(status: Optional[str] = None, limit: int = 50):
    """スケジュール一覧を取得"""
    try:
        schedules = scheduler.get_schedules(status=status, limit=limit)
        
        return [
            ScheduleResponse(
                id=schedule.id,
                post_id=schedule.post_id,
                scheduled_time=schedule.scheduled_time,
                schedule_type=schedule.schedule_type.value,
                status=schedule.status,
                created_at=schedule.created_at,
                executed_at=schedule.executed_at,
                error_message=schedule.error_message
            )
            for schedule in schedules
        ]
        
    except Exception as e:
        logger.error(f"スケジュール一覧の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: str):
    """スケジュールを取得"""
    try:
        schedule = scheduler.get_schedule(schedule_id)
        if schedule is None:
            raise HTTPException(status_code=404, detail="スケジュールが見つかりません")
        
        return ScheduleResponse(
            id=schedule.id,
            post_id=schedule.post_id,
            scheduled_time=schedule.scheduled_time,
            schedule_type=schedule.schedule_type.value,
            status=schedule.status,
            created_at=schedule.created_at,
            executed_at=schedule.executed_at,
            error_message=schedule.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"スケジュールの取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/schedules/{schedule_id}")
async def cancel_schedule(schedule_id: str):
    """スケジュールをキャンセル"""
    try:
        success = scheduler.cancel_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="スケジュールが見つからないか、キャンセルできません")
        
        logger.info(f"スケジュールをキャンセルしました: {schedule_id}")
        return {"message": "スケジュールをキャンセルしました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"スケジュールのキャンセルに失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedules/recurring", response_model=List[ScheduleResponse])
async def create_recurring_schedule(request: CreateRecurringScheduleRequest):
    """定期的なスケジュールを作成"""
    try:
        # スケジュール設定を作成
        from app.services.scheduler import ScheduleConfig, OptimalTimeSlot
        
        config = ScheduleConfig(
            schedule_type=ScheduleType(request.schedule_type),
            start_time=request.start_time,
            end_time=request.end_time,
            interval_hours=request.interval_hours,
            days_of_week=request.days_of_week,
            optimal_time_slots=[
                OptimalTimeSlot.MORNING,
                OptimalTimeSlot.EVENING
            ],
            max_posts_per_day=request.max_posts_per_day,
            enabled=True
        )
        
        # 定期的なスケジュールを作成
        schedules = scheduler.create_recurring_schedule(
            post_template=request.post_template,
            schedule_config=config
        )
        
        logger.info(f"定期的なスケジュールを作成しました: {len(schedules)}件")
        return [
            ScheduleResponse(
                id=schedule.id,
                post_id=schedule.post_id,
                scheduled_time=schedule.scheduled_time,
                schedule_type=schedule.schedule_type.value,
                status=schedule.status,
                created_at=schedule.created_at,
                executed_at=schedule.executed_at,
                error_message=schedule.error_message
            )
            for schedule in schedules
        ]
        
    except Exception as e:
        logger.error(f"定期的なスケジュールの作成に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=List[PostTemplateResponse])
async def get_templates():
    """投稿テンプレート一覧を取得"""
    try:
        templates = post_manager.get_templates()
        
        return [
            PostTemplateResponse(
                name=name,
                content_template=template.content_template,
                post_type=template.post_type.value,
                hashtags=template.hashtags,
                mentions=template.mentions,
                tone=template.tone,
                max_length=template.max_length,
                include_link=template.include_link,
                include_media=template.include_media
            )
            for name, template in templates.items()
        ]
        
    except Exception as e:
        logger.error(f"テンプレート一覧の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_name}", response_model=PostTemplateResponse)
async def get_template(template_name: str):
    """特定のテンプレートを取得"""
    try:
        templates = post_manager.get_templates()
        template = templates.get(template_name)
        
        if template is None:
            raise HTTPException(status_code=404, detail=f"テンプレートが見つかりません: {template_name}")
        
        return PostTemplateResponse(
            name=template_name,
            content_template=template.content_template,
            post_type=template.post_type.value,
            hashtags=template.hashtags,
            mentions=template.mentions,
            tone=template.tone,
            max_length=template.max_length,
            include_link=template.include_link,
            include_media=template.include_media
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"テンプレートの取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/templates/{template_name}", response_model=PostTemplateResponse)
async def update_template(template_name: str, request: UpdatePostTemplateRequest):
    """テンプレートを更新"""
    try:
        templates = post_manager.get_templates()
        template = templates.get(template_name)
        
        if template is None:
            raise HTTPException(status_code=404, detail=f"テンプレートが見つかりません: {template_name}")
        
        # 更新する項目のみ変更
        if request.content_template is not None:
            template.content_template = request.content_template
        if request.post_type is not None:
            template.post_type = PostType(request.post_type)
        if request.hashtags is not None:
            template.hashtags = request.hashtags
        if request.mentions is not None:
            template.mentions = request.mentions
        if request.tone is not None:
            template.tone = request.tone
        if request.max_length is not None:
            template.max_length = request.max_length
        if request.include_link is not None:
            template.include_link = request.include_link
        if request.include_media is not None:
            template.include_media = request.include_media
        
        # 保存
        post_manager.save_data()
        
        logger.info(f"テンプレートを更新しました: {template_name}")
        return PostTemplateResponse(
            name=template_name,
            content_template=template.content_template,
            post_type=template.post_type.value,
            hashtags=template.hashtags,
            mentions=template.mentions,
            tone=template.tone,
            max_length=template.max_length,
            include_link=template.include_link,
            include_media=template.include_media
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"テンプレートの更新に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_name}")
async def delete_template(template_name: str):
    """テンプレートを削除"""
    try:
        templates = post_manager.get_templates()
        
        if template_name not in templates:
            raise HTTPException(status_code=404, detail=f"テンプレートが見つかりません: {template_name}")
        
        del templates[template_name]
        post_manager.save_data()
        
        logger.info(f"テンプレートを削除しました: {template_name}")
        return {"message": f"テンプレート '{template_name}' を削除しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"テンプレートの削除に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/from-template/{template_name}", response_model=PostResponse)
async def create_post_from_template(template_name: str, variables: Optional[Dict[str, Any]] = None):
    """テンプレートから投稿を作成"""
    try:
        # テンプレートから投稿を作成
        post = post_manager.create_post_from_template(
            template_name=template_name,
            **(variables or {})
        )
        
        logger.info(f"テンプレートから投稿を作成しました: {post.id}")
        return PostResponse(
            id=post.id,
            content={
                "text": post.content.text,
                "image_url": post.content.image_url,
                "video_url": post.content.video_url,
                "hashtags": post.content.hashtags,
                "mentions": post.content.mentions,
                "links": post.content.links
            },
            scheduled_time=post.scheduled_time,
            status=post.status.value,
            post_type=post.post_type.value,
            template_name=post.template_name,
            created_at=post.created_at,
            updated_at=post.updated_at,
            posted_at=post.posted_at,
            error_message=post.error_message
        )
        
    except Exception as e:
        logger.error(f"テンプレートからの投稿作成に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """統計情報を取得"""
    try:
        stats = scheduler.get_statistics()
        return StatisticsResponse(**stats)
        
    except Exception as e:
        logger.error(f"統計情報の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimal-times")
async def get_optimal_times(date: Optional[datetime] = None, max_suggestions: int = 3):
    """最適な投稿時間を取得"""
    try:
        if date is None:
            date = datetime.now()
        
        optimal_times = scheduler.suggest_optimal_times(date, max_suggestions)
        return {"optimal_times": [time.isoformat() for time in optimal_times]}
        
    except Exception as e:
        logger.error(f"最適な投稿時間の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# テンプレート管理エンドポイント
@router.post("/templates", response_model=PostTemplateResponse)
async def create_template(request: PostTemplateRequest):
    """投稿テンプレートを作成"""
    try:
        template = PostTemplate(
            name=request.name,
            description=f"Template: {request.name}",  # デフォルトの説明
            content_template=request.content_template,
            post_type=PostType(request.post_type),
            hashtags=request.hashtags or [],
            mentions=request.mentions or [],
            tone=request.tone or "professional",
            max_length=request.max_length or 280,
            include_link=request.include_link,
            include_media=request.include_media,
            enabled=True
        )
        
        post_manager.add_template(request.name, template)
        
        logger.info(f"テンプレートを作成しました: {request.name}")
        return PostTemplateResponse(
            name=request.name,
            content_template=template.content_template,
            post_type=template.post_type.value,
            hashtags=template.hashtags,
            mentions=template.mentions,
            tone=template.tone,
            max_length=template.max_length,
            include_link=template.include_link,
            include_media=template.include_media
        )
        
    except Exception as e:
        logger.error(f"テンプレートの作成に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 