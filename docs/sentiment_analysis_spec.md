# 感情分析スコア仕様書

## 1. 概要

感情分析スコアは、YouTube動画のコメントに対する感情分析を行い、視聴者の反応を数値化する指標です。
このスコアは、動画のバズり度を評価する重要な要素の一つとして使用されます。

## 2. スコアの範囲

- 基本スコア: -1.0 から 1.0
  - -1.0: 最もネガティブな感情
  - 0.0: ニュートラルな感情
  - 1.0: 最もポジティブな感情

- 正規化スコア: 0 から 10
  - 0: 最もネガティブな感情
  - 5: ニュートラルな感情
  - 10: 最もポジティブな感情

## 3. 計算方法

### 3.1 基本スコアの計算

1. 各コメントの感情分析
   - TextBlobライブラリを使用
   - 各コメントの感情極性（polarity）を取得
   - 範囲: -1.0 から 1.0

2. 平均スコアの計算
   ```python
   avg_sentiment = np.mean(sentiments)
   ```

### 3.2 正規化スコアの計算

基本スコアを0-10の範囲に変換：
```python
normalized_score = (sentiment_score + 1) * 5
```

## 4. 感情分布の分類

### 4.1 感情カテゴリ

- ポジティブ: スコア > 0.1
- ニュートラル: -0.1 ≤ スコア ≤ 0.1
- ネガティブ: スコア < -0.1

### 4.2 分布の計算

```python
positive = len([s for s in sentiments if s > 0.1]) / len(sentiments)
neutral = len([s for s in sentiments if -0.1 <= s <= 0.1]) / len(sentiments)
negative = len([s for s in sentiments if s < -0.1]) / len(sentiments)
```

## 5. 主要感情の判定

以下の優先順位で判定：
1. ポジティブ > ニュートラル かつ ポジティブ > ネガティブ → "positive"
2. ネガティブ > ニュートラル かつ ネガティブ > ポジティブ → "negative"
3. その他 → "neutral"

## 6. エラー処理

### 6.1 コメントが存在しない場合
- 基本スコア: 0.0
- 正規化スコア: 5.0
- 感情分布: すべて0.0
- 主要感情: "neutral"

### 6.2 分析エラーの場合
- エラーログの記録
- デフォルト値の返却（上記と同様）

## 7. 使用例

```python
# 感情分析の実行
sentiment_analysis = analyze_sentiment(video)

# 結果の取得
sentiment_score = sentiment_analysis["sentiment_score"]  # -1.0 から 1.0
distribution = sentiment_analysis["sentiment_distribution"]  # 各感情の割合
dominant = sentiment_analysis["dominant_sentiment"]  # 主要な感情
```

## 8. 注意事項

1. 言語依存性
   - 現在は英語と日本語のコメントに対応
   - 他の言語の場合は精度が低下する可能性あり

2. 文脈の考慮
   - 単純な感情極性のみを考慮
   - 文脈や皮肉などの複雑な表現は考慮しない

3. エモジの扱い
   - テキストベースの分析のみ
   - エモジの感情は考慮しない

## 9. 今後の改善点

1. 多言語対応の強化
2. エモジ分析の追加
3. 文脈を考慮した分析
4. 機械学習モデルの導入
5. カスタム辞書の作成

## 7. バズり度スコア仕様

### 7.1 概要
バズり度スコアは、動画の総合的な人気度を評価する指標です。
視聴回数、エンゲージメント、コメント、チャンネル影響力、感情分析の5つの要素から構成されます。

### 7.2 スコアの構成要素

1. 視聴回数スコア（0-30点）
   - 基本スコア: 視聴回数に基づく評価（0-20点）
     - 10万回視聴で20点
     - それ以上は20点固定
   - 成長率スコア: 視聴回数の増加率に基づく評価（0-10点）
     - 1時間あたりの視聴回数増加率を計算
     - 最大10点

2. エンゲージメントスコア（0-25点）
   - いいね率スコア（0-15点）
     - いいね数/視聴回数 × 15
   - コメント率スコア（0-10点）
     - コメント数/視聴回数 × 10

3. コメント活性度スコア（0-20点）
   - コメント数スコア（0-10点）
     - 1000コメントで10点
     - それ以上は10点固定
   - コメント質スコア（0-10点）
     - コメントの長さ
     - 感情分析スコア
     - 返信数
     - いいね数

4. チャンネル影響力スコア（0-15点）
   - チャンネル登録者数（0-5点）
   - 過去動画の平均視聴回数（0-5点）
   - チャンネルの総再生回数（0-5点）

5. 感情分析スコア（0-10点）
   - コメントの感情分析結果を0-10点に正規化

### 7.3 計算方法

```python
def calculate_buzz_score(video: TrendVideo) -> float:
    # 視聴回数スコア
    view_score = min(
        (video.stats.view_count / 100000 * 20) + 
        (calculate_view_growth(video) * 10),
        30
    )

    # エンゲージメントスコア
    like_rate = video.stats.like_count / video.stats.view_count
    comment_rate = video.stats.comment_count / video.stats.view_count
    engagement_score = min(
        (like_rate * 15) + (comment_rate * 10),
        25
    )

    # コメント活性度スコア
    comment_quality = analyze_comment_quality(video)
    comment_score = min(
        (video.stats.comment_count / 1000 * 10) + 
        (comment_quality * 10),
        20
    )

    # チャンネル影響力スコア
    channel_score = calculate_channel_score(video)

    # 感情分析スコア
    sentiment_score = calculate_sentiment_score(video)

    # 合計スコア
    total_score = (
        view_score + 
        engagement_score + 
        comment_score + 
        channel_score + 
        sentiment_score
    )

    return min(total_score, 100)
```

### 7.4 エラー処理

1. データ不足の場合
   - 各要素のスコアは0点とする
   - ログに警告を記録

2. 計算エラーの場合
   - エラーが発生した要素のスコアは0点とする
   - エラーの詳細をログに記録
   - 他の要素の計算は継続

3. 異常値の処理
   - 負の値は0点として扱う
   - 上限値を超える値は上限値として扱う

### 7.5 データ更新頻度

1. 視聴回数、いいね数、コメント数
   - 1時間ごとに更新
   - 履歴データを保持（30日間）

2. チャンネル情報
   - 24時間ごとに更新
   - 履歴データを保持（90日間）

3. コメント分析
   - 新規コメント発生時に更新
   - 感情分析は1時間ごとに再計算

### 7.6 パフォーマンス考慮事項

1. キャッシュ戦略
   - スコアの計算結果を1時間キャッシュ
   - チャンネル情報を24時間キャッシュ

2. バッチ処理
   - 大量の動画のスコア計算はバッチ処理
   - 優先度の高い動画は即時計算

3. データベース最適化
   - インデックスの適切な設定
   - パーティショニングの検討 