enemy_config = {
    "type": "tank",
    "hp": 5000,
    "atk": 100,
    "speed": 1,
    "color": (128, 128, 128),
    "attack_range": 270,
    "is_aoe": True,
    "kb_limit": 5,
    "width": 230,
    "height": 230,
    "windup_duration": 200,
    "attack_duration": 100,
    "recovery_duration": 200,
    "attack_interval": 8000,
    "idle_frames": ["enemy_folder/tank/walking/tank_enemy_walking_1.png"],
    "move_frames": [f"enemy_folder/tank/walking/tank_enemy_walking_{i}.png" for i in range(1, 3)],
    "windup_frames": [f"enemy_folder/tank/attacking/tank_enemy_attacking_{i}.png" for i in range(1, 3)],
    "attack_frames": ["enemy_folder/tank/attacking/tank_enemy_attacking_3.png"],
    "recovery_frames": [f"enemy_folder/tank/attacking/tank_enemy_attacking_{i}.png" for i in range(1, 3)],
    "kb_frames": ["enemy_folder/tank/walking/tank_enemy_walking_1.png"],
    "attributes": ["古"],  # Metal and Relic, based on gray color and boss status
    "reward": 13200,  # 假設的獎勵值
    "attack_type": "gun",  # 攻擊類型
}