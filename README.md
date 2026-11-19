# 🏡 room-storage-designer (出租屋空间收纳 3D 规划与版本管理系统)

> 专门针对**租房族、小户型及多杂物场景（羽毛球装备、宠物猫粮、零食、快递纸箱）**的 1:1 真实比例 3D WebGL 空间规划与采购决策系统。

---

## 🌟 核心特性

1. **绝对建筑刚性（Anti-Hallucination Invariance）**
   * 严厉杜绝 AI 图像随意篡改户型的通病。门朝向、窗户采光面、床架与书桌的相对物理坐标 **100% 绝对锁死**。
2. **1:1 毫米级工程物理尺度**
   * 严格遵循 `1 Three.js 单位 = 真实 1 米`；
   * 严格执行《住宅设计规范》（GB 50096）主过道 $\ge 85\text{cm}$ 畅通动线要求；
   * 严格匹配国标单开室内门（$90\text{cm} \times 210\text{cm}$）与标准家具尺寸。
3. **多版本管理体系（Semantic Design Versioning）**
   * 内置 `v1.0` 到 `v2.2` 四套风格版本一键平滑切换，实时联动 3D 材质、灯光与动态采购清单（BOM）：
     * **v1.0-Basic 基础免打孔实用版**（¥164）：超薄门背挂架 + 移动碳钢推车 + 床底双向滑轮扁箱。
     * **v2.0-Tech 黑金机能·潮流运动极客版**（¥1,150，**当前主干版本**）：冷轧钢重型洞洞板 + 球拍斜插展陈 + 3000K 暖光线灯 + 深灰阻燃地毯。
     * **v2.1-Camping 都市山系·露营游牧版**（¥980）：侧开折叠箱组 + 剑麻耐抓毯 + 墙面原木猫道跑道（搬家零打包）。
     * **v2.2-MUJI 日式暖木·MUJI 治愈原木版**（¥1,080）：宜家 BOAXEL 悬空轨道架 + 磨砂半透抽屉 + 奶白遮光帘。
4. **原照片点对点施工批注**
   * 内置 Python 自动化批注脚本，直接在用户上传的照片上生成带指示线与规格卡片的施工蓝图。
5. **退租无痕交房保障**
   * 配套 9.9 元无痕补墙膏工法，打孔上墙也能在 5 分钟内彻底抹平，押金全退。

---

## 📂 项目结构

```
room-storage-designer/
├── index.html                   # 核心 1:1 真实比例 3D WebGL 交互看板（支持版本一键切换）
├── comparison.html              # 改造前后无缝滑动对比工具 (Before & After)
├── SKILL.md                     # Antigravity / AI Agent 标准技能定义文档
├── scripts/
│   └── annotate_room.py         # 实景照片空间动线与收纳位点对点批注脚本
├── libs/                        # 离线 3D 渲染核心库 (Three.js, OrbitControls, Tween.js)
│   ├── three.min.js
│   ├── OrbitControls.js
│   └── tween.umd.js
├── assets/                      # 实景参考照、改造效果图与批注蓝图
│   ├── cluttered_chinese_rental_room_1795068770948.jpg
│   ├── organized_room_after_makeover_1795069166491.jpg
│   └── annotated_room_blueprint.jpg
└── README.md
```

---

## 🚀 快速启动

在本地任何终端中进入项目目录，启动轻量 HTTP 服务即可秒开：

```bash
# 启动本地服务
python3 -m http.server 8080

# 打开 3D 交互看板
open http://localhost:8080/index.html

# 打开改造前后滑动对比看板
open http://localhost:8080/comparison.html
```

---

## 🛠️ 自动化原图标注脚本使用

```bash
python3 scripts/annotate_room.py <输入房间照片.jpg> <标注配置.json> <输出施工蓝图.jpg>
```

---

## 📄 授权与归属
* Author: **maomao19950101 / harry** (584800267@qq.com)
* License: Private / Proprietary
