# 实拍房间照片空间反推与 `room_spec.json` 建模指南

从单张或多张用户实拍出租屋照片中，精准提取建筑刚性骨架与杂物坐标，输出供 `scripts/audit_room_spec.py` 与 `templates/3d_room_viewer.html` 消费的标准配置文件。

---

## 1. 单图几何比例反推三锚点 (Photo Scale Calibration)

在缺少卷尺测量的照片中，利用建筑固定国标参照物反推房间长宽高与净空：

1. **标准室内单开门（第一绝对尺度锚点）**：
   - 常见入户/卧室木门：`宽 0.86m (含套 0.90m) × 高 2.05m`；把手中心离地约 `1.00m`。
   - 用门高度作为 `Y` 轴像素标尺，可立刻推算出层高 (`2.55m ~ 2.75m`) 与门边壁挂允许净空。
2. **地面铺装地砖网格（水平 `XZ` 地板坐标计算器）**：
   - 常见出租屋瓷砖为 **`600×600 mm`** 或 **`800×800 mm`**；数清垂直/横向完整地砖格数即可推算出房间净宽 `W`（如 6 块 600 砖 = `3.6m`）与净深 `D`（如 8 块 600 砖 = `4.8m`）。
3. **标准家具尺寸校正**：
   - 双人床常用 `1.5m × 2.0m`（少数 `1.2m` 或 `1.8m`），书桌常见 `1.0m ~ 1.2m × 0.6m`，床下抽屉区可用高度取决于床腿高度（常见 `12cm / 18cm / 22cm`）。

---

## 2. 坐标系约定 (Right-Handed Y-Up Metrics: 1 unit = 1 meter)

- 原点 `(0, 0, 0)` 位于**房间地板正中心**，`Y = 0` 为地砖表面。
- 墙体方位与内净界：
  - **North (-Z)**：`Z = -depth / 2`（内面 `-depth/2 + 0.08`）
  - **South (+Z)**：`Z = +depth / 2`（内面 `+depth/2 - 0.08`）
  - **West  (-X)**：`X = -width / 2`（内面 `-width/2 + 0.08`）
  - **East  (+X)**：`X = +width / 2`（内面 `+width/2 - 0.08`）

---

## 3. `room_spec.json` 标准结构示例

完整示范模板见 [templates/room_spec.default.json](../templates/room_spec.default.json)：

```json
{
  "meta": {
    "title": "主卧单间出租屋 1:1 收纳重构",
    "unit": "meters",
    "styleDefault": "muji"
  },
  "room": {
    "width": 3.6,
    "depth": 4.8,
    "height": 2.6,
    "cutawaySides": ["east", "south"]
  },
  "door": {
    "wall": "west",
    "offset": -1.65,
    "width": 0.90,
    "height": 2.10,
    "swing": "inward-north"
  },
  "window": {
    "wall": "north",
    "offset": 0.50,
    "width": 1.80,
    "sillHeight": 0.85,
    "height": 1.30
  },
  "bed": {
    "x": 0.90,
    "z": -1.25,
    "width": 1.52,
    "length": 2.02,
    "clearance": 0.22,
    "rotY": 0,
    "underDrawerSide": "west"
  },
  "furniture": {
    "desk": { "x": -1.10, "z": 0.60, "width": 1.20, "depth": 0.60, "rotY": 0 },
    "chair": { "x": -1.10, "z": 1.15, "rotY": 0 },
    "wardrobe": { "x": 1.43, "z": 0.85, "width": 0.52, "length": 1.28, "rotY": 0 },
    "catStation": { "x": -1.48, "z": -0.45, "rotY": 0 },
    "racketMount": { "x": -1.70, "z": -0.60, "hookY": 1.80, "rotY": 0 },
    "rug": { "x": -0.18, "z": 0.68, "width": 1.00, "length": 1.95 }
  }
}
```
