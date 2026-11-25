#!/usr/bin/env python3
"""
Xianyu Idle-Asset Triage & Anti-Dispute Listing Generator
Reads a declutter_spec JSON + optional --bom-total and prints:
  1) Copy-paste ready Xianyu listing cards (anti-dispute local pickup)
  2) Net recovery budget offset summary
  3) Optional HTML fragment for before_after_slider / dashboard injection
"""

import argparse
import html
import json
import sys


def build_listing_text(item):
    name = item["name"]
    defect = item.get("condition", "自用闲置")
    price = item.get("listPrice", item.get("minPrice", 0))
    landmark = item.get("landmark", "同城地铁站/小区门口")
    pickup_only = item.get("pickupOnly", True)

    mode_str = "仅限同城自提（大件免折腾不邮寄）" if pickup_only else "同城自提优先 / 支持发快递"
    return (
        f"【{name}｜{defect}】\n"
        f"价格：¥{price}（爽快自取可小刀）\n"
        f"真实说明：{item.get('description', defect)}，现场看实物或提前拍清晰细节图。\n"
        f"取货方式：{mode_str}，地点约在【{landmark}】，工作日下班后或周末均可。\n"
        f"售后声明：闲置/配件按描述实况出，当面验看拿走，售出后不退不换。"
    )


def render_html_rows(items):
    rows = []
    for idx, it in enumerate(items, 1):
        tier = it.get("tier", "闲鱼回血")
        p_min = int(it.get("minPrice", 0))
        p_max = int(it.get("maxPrice", p_min))
        price_str = f"¥{p_min}" if p_min == p_max else f"¥{p_min}~{p_max}"
        copy_txt = html.escape(build_listing_text(it)).replace("\n", "&#10;")
        rows.append(
            f"<tr>"
            f"<td>{idx}</td>"
            f"<td><span class='badge'>{html.escape(tier)}</span></td>"
            f"<td>{html.escape(it['name'])}</td>"
            f"<td>{html.escape(it.get('condition', ''))}</td>"
            f"<td class='price'>{price_str}</td>"
            f"<td><button class='tab-btn copy-btn' style='padding:4px 10px;font-size:12px;' data-copy=\"{copy_txt}\" onclick=\"navigator.clipboard.writeText(this.dataset.copy);this.textContent='已复制✓';setTimeout(()=>this.textContent='复制闲鱼文案',1600)\">复制闲鱼文案</button></td>"
            f"</tr>"
        )
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description="Generate Xianyu idle recovery listings and net budget.")
    parser.add_argument("declutter_json", help="Path to JSON list or {items: [...]} spec")
    parser.add_argument("--bom-total", type=int, default=0, help="Total storage BOM spend (RMB)")
    parser.add_argument("--html-out", help="Optional path to save HTML table rows fragment")
    args = parser.parse_args()

    with open(args.declutter_json, "r", encoding="utf-8") as f:
        raw = json.load(f)
    items = raw["items"] if isinstance(raw, dict) else raw

    tot_min = sum(int(i.get("minPrice", 0)) for i in items)
    tot_max = sum(int(i.get("maxPrice", i.get("minPrice", 0))) for i in items)

    print("=== 闲鱼闲置出清与回血台账 ===")
    for idx, it in enumerate(items, 1):
        p_min = int(it.get("minPrice", 0))
        p_max = int(it.get("maxPrice", p_min))
        print(f"\n[{idx}] {it['name']} ({it.get('tier', '闲鱼回血')}) | 预估回血: ¥{p_min}~¥{p_max}")
        print("--- 可直接复制挂闲鱼文案 ---")
        print(build_listing_text(it))

    print("\n=== 净预算抵扣汇总 ===")
    print(f"改造采购总额: ¥{args.bom_total}")
    print(f"预计闲鱼回血: ¥{tot_min} ~ ¥{tot_max}")
    net_hi = args.bom_total - tot_min
    net_lo = args.bom_total - tot_max
    if net_lo <= 0:
        print(f"净实际支出: ¥0 甚至倒赚 +¥{abs(net_lo)} (最高少花 ¥{tot_max})")
    else:
        print(f"净实际支出: ¥{net_lo} ~ ¥{net_hi}")

    if args.html_out:
        with open(args.html_out, "w", encoding="utf-8") as f:
            f.write(render_html_rows(items))
        print(f"\nSaved HTML rows -> {args.html_out}")


if __name__ == "__main__":
    main()
