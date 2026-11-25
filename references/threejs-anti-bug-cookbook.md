# Three.js 3D 室内建模与反穿模工程手册 (Anti-Bug Cookbook)

> 整理自 GitHub `CloudAI-X/threejs-skills` 最佳实践与实测压测踩坑复盘。编写或扩展 3D 室内组件时必须逐条核对。

---

## 1. 建筑门套与窗户（严禁“闹鬼门”）

- ❌ **禁止**：用一个实心 `BoxGeometry` 当门套 (`architrave`) —— 门扇旋转打开后，实心盒子还死死堵在门框里像两扇门。
- ✅ **正确**：门框必须用 **3 根独立框料拼合**：左门挺 (`jambRear`) + 右门挺 (`jambFront`) + 门头横梁 (`jambTop`) + 金属门槛条 (`threshold`)，中间彻底镂空。
- **门外走廊补全**：在门洞外侧必须构建有暖色照明走廊地板、背墙与小壁灯，保证开门后透出明亮生活空间而非黑洞虚空。
- **门底缝隙**：门扇底部 `min.y` 应离地 `0.014 ~ 0.018 m`，彻底高于门口地垫 (`0.008 m`)，开门时绝不刮擦门垫。

---

## 2. 智能自动剖切外墙 (Smart Auto-Cutaway Walls)

- **痛点**：如果将近侧两面墙永久削成 10cm 矮边，虽然全景好看，但一旦推近看室内衣柜/书桌，家具背后全是漆黑的宇宙背景。
- **标准解法**：保留真实 `2.6 m` 全高墙面组 (`wallFullGroup`) 与地板矮沿 (`curb`) 叠放，在 `animate()` 中根据摄影机坐标实时显隐：
  ```javascript
  eastWallFullGroup.visible  = (camera.position.x <  roomHalfW - 0.15);
  southWallFullGroup.visible = (camera.position.z <  roomHalfD - 0.15);
  ```
  全屋俯瞰自动隐墙；室内平视自动闭合为完整墙面+踢脚线+电源插座。

---

## 3. 父子局部坐标系 & 地面零悬空原则

- ❌ **绝对禁止**：把桌面书籍、显示器、收纳盒直接按世界坐标扔进根场景 —— 只要书桌位移 10cm，桌上物品立刻变成半空漂浮物。
- ✅ **强制父子挂载**：任何搁置在家具表面上的小件（书立、台灯、水杯、键盘、手表托盘）**必须 `deskGroup.add(child)` / `wardrobeGroup.add(child)`**，局部 `Y = 支撑台面顶面高度`！
- **中心旋转包装器 (`Root -> Group`)**：需要支持用户 90° 旋转/拖拽的组合家具（如衣柜、猫咪区），在外层包裹中心枢轴组：
  ```javascript
  const root = new THREE.Group();
  root.position.set(cx, 0, cz);
  innerGroup.position.set(-cx, 0, -cz);
  root.add(innerGroup);
  ```
  旋转 `root.rotation.y` 时严格绕自身几何中心转动，且热区标签使用 `anchorObj.localToWorld(localOffset)` 自动跟随。

---

## 4. 欧拉角与局部精雕防踩坑清单

1. **衣柜背部 X 型抗晃剪刀撑（Euler XYZ 陷阱）**：
   - 在与 YZ 平面平行的背墙 (`X = const`) 上做对角斜拉杆，默认垂直于 Y 轴的 `CylinderGeometry` 只需绕 **X 轴**单轴倾角 `rotation.x = ±atan2(dz, dy)`！
   - ❌ 严禁同时设 `rotation.z = PI/2` 和 `rotation.y = angle`，那会把拉杆直挺挺插向房间走道与衣物内部！
2. **中空容器必须用 `LatheGeometry` 或分板拼接**：
   - 猫咪陶瓷食水碗用 `LatheGeometry` 定义内外壁折线，切勿用实心圆柱体盖死碗内干粮/水面；
   - 桌面透明亚克力书立用 **底板 + 背板 + 侧竖挡板 + 中分格板** 拼接开放卡槽，严禁把书插在全封闭透明实心立方体里；
   - MUJI 半透抽屉柜用 **背板 + 层板 + 竖格板** 构造 6 个真实开放格口，再把磨砂半透门板和内置彩色叠衣放进去。
3. **排除模糊阴影片的紧致 `Box3` (`getTightBox`)**：
   - 地面渐变接触阴影贴图 (`addContactShadow`) 通常比家具底座大 `10~15 cm`；务必给阴影平面标记 `userData.isShadow = true`，计算摆位碰撞和 `Box3Helper` 时跳过阴影面，避免贴墙 2cm 时误报穿墙红线。
4. **床下扁箱三维尺寸联动**：
   - `drawerTotalY = wheelDia + tubHeight + lidThickness` 必须小于 `bedClearance - 0.02m`，滑轨路线 `X/Z` 需绕开床腿坐标及地毯厚缘。
5. **交互点击防拖拽误触 & ID 映射**：
   - 射线检测点击弹窗必须比较 `pointerdown -> pointerup` 位移 `< 5px`，防止拖拽旋转视角后误触弹窗；
   - 热区详情严禁用硬编码数组下标 (`hotspotsData[0]`)，必须用键值映射 (`hotspotsById['hs-xxx']`)。
