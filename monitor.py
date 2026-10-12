import akshare as ak
import time
import requests

# ========== 配置区 ==========
# 把你的飞书 Webhook 地址填在这里（没配置就留空，程序会只在屏幕打印）
FEISHU_WEBHOOK = ""

# 监控列表：代码要用 sh / sz 前缀
watchlist = {
    "sh600021": {"name": "上海电力", "upper": 20, "lower": 10},
    # 想加更多股票就照着上面这行写，注意末尾要有逗号
    # "sz000001": {"name": "平安银行", "upper": 12, "lower": 10},
}

# ========== 飞书推送函数 ==========
def send_feishu_alert(message):
    if not FEISHU_WEBHOOK:
        print("（未配置飞书 Webhook，仅屏幕提醒）")
        return
    headers = {"Content-Type": "application/json"}
    data = {"msg_type": "text", "content": {"text": message}}
    try:
        requests.post(FEISHU_WEBHOOK, json=data, headers=headers, timeout=10)
        print("飞书提醒已发送。")
    except Exception as e:
        print(f"发送飞书提醒失败: {e}")

# ========== 核心监控逻辑 ==========
def check_prices():
    try:
        spot_df = ak.stock_zh_a_spot()   # 新浪全市场实时行情
    except Exception as e:
        print(f"获取实时行情失败: {e}")
        return

    for code, info in watchlist.items():
        try:
            stock_row = spot_df[spot_df["代码"] == code]
            if stock_row.empty:
                print(f"未找到 {info['name']} ({code}) 的行情。")
                continue

            current_price = float(stock_row["最新价"].values[0])
            change_pct = stock_row["涨跌幅"].values[0]

            print(f"{info['name']} ({code}): 最新价 {current_price}, 涨跌幅 {change_pct}%")

            if current_price > info["upper"]:
                msg = f"⚠️ {info['name']} 突破上限 {info['upper']}，当前价 {current_price}"
                print(msg)
                send_feishu_alert(msg)
            elif current_price < info["lower"]:
                msg = f"⚠️ {info['name']} 跌破下限 {info['lower']}，当前价 {current_price}"
                print(msg)
                send_feishu_alert(msg)

        except Exception as e:
            print(f"处理 {info['name']} 时出错: {e}")

# ========== 主循环 ==========
if __name__ == "__main__":
    print("开始监控自选股，按 Ctrl+C 停止...")
    while True:
        check_prices()
        print("-" * 40)
        time.sleep(180)   # 每 3 分钟检查一次，避免请求太频繁被限流