cat_config = {
    "hp": 600,
    "atk": 120,
    "speed": 4,
    "color": (0, 255, 255),
    "attack_range": 200,
    "is_aoe": False,
    "kb_limit": 3,
    "cooldown": 8000,
    "cost": 150,
    "width": 100,
    "height": 100,
    "windup_duration": 200,
    "attack_duration": 100,
    "recovery_duration": 200,
    "idle_frames": ["cat_folder/speedy/walking/speedy.png"] * 100,
    "move_frames": [f"cat_folder/eraser/walking/processed_frame_0001.png"],
    "windup_frames": [f"cat_folder/eraser/attacking/processed_frame_000{i}.png" for i in range(7, 10)] \
        +[f"cat_folder/eraser/attacking/processed_frame_00{i}.png" for i in range(10, 17)],
    "attack_frames": [f"cat_folder/eraser/attacking/processed_frame_00{i}.png" for i in range(17, 24)],
    "recovery_frames": [f"cat_folder/eraser/attacking/processed_frame_00{i}.png" for i in range(24, 26)],
    "kb_frames": []
}