enemy_config = {
    "type": "fast",
    "hp": 600,
    "atk": 8,
    "speed": 4,
    "color": (0, 255, 0),
    "attack_range": 45,
    "is_aoe": False,
    "kb_limit": 7,
    "width": 200,
    "height": 200,
    "windup_duration": 100,
    "attack_duration": 100,
    "recovery_duration": 100,
    "attack_interval": 2000,
    "idle_frames": ["enemy_folder/fast/walking/fast_enemy_walking.png"],
    "move_frames": [f"enemy_folder/fast/walking/fast_enemy_walking_{i}.png" for i in range(1, 3)],
    "windup_frames": ["enemy_folder/fast/attacking/fast_enemy_attacking_1.png"],
    "attack_frames": ["enemy_folder/fast/attacking/fast_enemy_attacking_2.png"],
    "recovery_frames": ["enemy_folder/fast/attacking/fast_enemy_attacking_1.png"],
    "kb_frames": ["enemy_folder/fast/walking/fast_enemy_walking.png"],
    "attributes": ["異", "天"],  # Alien and Angel, based on fast type and green color
    "reward": 187,  # 假設的獎勵值
    "attack_type":"physic",  # 攻擊類型
}