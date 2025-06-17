cat_config = {
    "hp": 600,
    "atk": 10,
    "speed": 4,
    "color": (0, 255, 255),
    "attack_range": 170,
    "is_aoe": True,
    "kb_limit": 3,
    "cooldown": 1000,
    "cost": 80,
    "width":80,
    "height": 150,
    "windup_duration": 200,
    "attack_duration": 100,
    "recovery_duration": 200,
    "attack_interval": 3000,
    "idle_frames": ["cat_folder/eraser/walking/processed_frame_0001.png"] * 900,
    "move_frames": [f"cat_folder/eraser/walking/processed_frame_0001.png"],
    "windup_frames": [f"cat_folder/eraser/attacking/processed_frame_000{i}.png" for i in range(7, 10)] \
        +[f"cat_folder/eraser/attacking/processed_frame_00{i}.png" for i in range(10, 17)],
    "attack_frames": [f"cat_folder/eraser/attacking/processed_frame_00{i}.png" for i in range(17, 24)],
    "recovery_frames": [f"cat_folder/eraser/attacking/processed_frame_00{i}.png" for i in range(24, 26)],
    "kb_frames": [],
    "delta_y": -42, # 微調 y 座標
    "ibtn_idle": "cat_folder/eraser/ibtn_idle.png",
    "ibtn_hover": "ccat_folder/eraser/ibtn_hover.png",
    "ibtn_pressed": "cat_folder/eraser/ibtn_pressed.png",
    "attack_type": "physic",  # 攻擊類型
    "attack_type": "physic",  # 攻擊類型
    "cat_image": "cat_folder/eraser/cat_image.png",  # 放在levelselection的貓咪圖片
}