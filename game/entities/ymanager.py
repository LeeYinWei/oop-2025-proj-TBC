
class YManager:
    def __init__(self, base_y=450, min_y=360, max_slots=30):
        self.base_y = base_y        # 螢幕底部
        self.min_y = min_y          # 不會比這還高
        self.max_slots = max_slots  # 最多幾個 slot
        self.occupied = set()

    def calculate_y(self, index):
        # 使用類似等比或反比縮小距離，這裡用簡單對數為例
        import math
        y = self.base_y-2.7*(index)**0.5
        return max(self.min_y, y)

    def get_available_y(self):
        for i in range(self.max_slots):
            if i not in self.occupied:
                self.occupied.add(i)
                #print(f"YManager: Allocated slot {i} at y={self.calculate_y(i)}")
                return self.calculate_y(i), i
        return self.calculate_y(self.max_slots-1), -1  # fallback

    def release_y(self, index):
        self.occupied.discard(index)
        #print(f"YManager: Released slot {index}")
