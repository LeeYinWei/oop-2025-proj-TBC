cat_config = {
    "hp": 600,
    "atk": 15,
    "speed": 1.5,
    "color": (255, 0, 255),
    "attack_range": 200,
    "is_aoe": True,
    "kb_limit": 3,
    "cooldown": 9000,
    "cost": 230,
    "width": 220,
    "height": 220,
    "windup_duration": 200,
    "attack_duration": 400,
    "recovery_duration": 200,
    "attack_interval": 3000,
    "idle_frames": ["cat_folder/mtank/walking/mtank.png"],
    "move_frames": ["cat_folder/mtank/walking/mtank.png",
                    "cat_folder/mtank/walking/mtank-walking1.png",
                    "cat_folder/mtank/walking/mtank-walking2.png",
                    "cat_folder/mtank/walking/mtank-walking1.png",],
    "windup_frames": ["cat_folder/mtank/attacking/mtank-attacking1.png",
                      "cat_folder/mtank/attacking/mtank-attacking2.png"],
    "attack_frames": ["cat_folder/mtank/attacking/mtank-attacking3.png",
                      "cat_folder/mtank/attacking/mtank-attacking4.png",
                      "cat_folder/mtank/attacking/mtank-attacking5.png",
                      "cat_folder/mtank/attacking/mtank-attacking4.png",
                      "cat_folder/mtank/attacking/mtank-attacking3.png"],
    "recovery_frames": ["cat_folder/mtank/attacking/mtank-attacking2.png",
                        "cat_folder/mtank/attacking/mtank-attacking1.png"],
    "kb_frames": [],
    "ibtn_idle": "cat_folder/mtank/ibtn_idle.png",
    "ibtn_hover": "ccat_folder/mtank/ibtn_hover.png",
    "ibtn_pressed": "cat_folder/mtank/ibtn_pressed.png",
    "attack_type":"gas",
    "cat_image": "cat_folder/mtank/cat_image.png",  # 放在levelselection的貓咪圖片
}