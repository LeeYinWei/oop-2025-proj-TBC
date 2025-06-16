enemy_config = {
    "type": "basic",
    "hp": 1000,
    "atk": 10,
    "speed": 2,
    "color": (255, 0, 0),
    "attack_range": 100,
    "is_aoe": False,
    "kb_limit": 5,
    "width": 200,
    "height": 200,
    "windup_duration": 200,
    "attack_duration": 100,
    "recovery_duration": 200,
    "attack_interval": 3000,
    "idle_frames": ["enemy_folder/basic/walking/basic_enemy.png"],  # 使用 basic_enemy.png 作為 idle 狀態
    "move_frames": [
        "enemy_folder/basic/walking/basic_enemy_walking_1.png",
        "enemy_folder/basic/walking/basic_enemy_walking_2.png",
        "enemy_folder/basic/walking/basic_enemy_walking_3.png",
        "enemy_folder/basic/walking/basic_enemy_walking_4.png",
        "enemy_folder/basic/walking/basic_enemy_walking_5.png",
        "enemy_folder/basic/walking/basic_enemy_walking_6.png"
    ],  # 行走動畫序列
    "windup_frames": [],  # 無對應圖片，保持空
    "attack_frames": ["enemy_folder/basic/attacking/basic_enemy_attacking.png"],  # 攻擊動畫
    "recovery_frames": [],  # 無對應圖片，保持空
    "kb_frames": [],  # 無對應圖片，保持空
    "attributes": ["紅"],  # Fixed attribute: Red, based on color (255, 0, 0)
    "reward": 105,  # 假設的獎勵值
    "attack_type":"gun",  # 攻擊類型
}