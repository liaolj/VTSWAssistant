# Silero VAD 参数调优

## 推荐起点
- threshold: 0.58
- min_silence_ms: 800
- max_segment_ms: 5000
- sample_rate: 16000, frame_ms: 20

## 环境建议
- 安静办公室：threshold 0.55–0.60
- 轻噪咖啡厅：0.60–0.65；考虑启用 PTT（按住说话）
- 车厢/风扇噪声：0.65+；min_silence_ms 提高到 1000–1200

## 观测指标
- 误触段数（越少越好）
- 平均段长（2–5 秒最佳）
- 回溯截断率（段尾被截短）
