import akshare as ak
import time
from datetime import datetime

# ========== 配置区 ==========
watchlist = {
    "sh600021": {"name": "上海电力", "upper": 20, "lower": 10},
    # "sz000001": {"name": "平安银行", "upper": 12, "lower": 10},
}

# ========== 核心监控逻辑 ==========
def check_prices():
    try:
        spot_df = ak.stock_zh_a_spot()   # 新浪全市场实时行情
    except Exception as e:
        print(f"获取实时行情失败: {e}")
        return

    results = []
    for code, info in watchlist.items():
        try:
            stock_row = spot_df[spot_df["代码"] == code]
            if stock_row.empty:
                results.append(f"未找到 {info['name']} ({code}) 的行情。")
                continue

            current_price = float(stock_row["最新价"].values[0])
            change_pct = stock_row["涨跌幅"].values[0]
            status = "正常"

            if current_price > info["upper"]:
                status = f"⚠️ 突破上限 {info['upper']}"
            elif current_price < info["lower"]:
                status = f"⚠️ 跌破下限 {info['lower']}"

            results.append(f"{info['name']} ({code}): 最新价 {current_price}, 涨跌幅 {change_pct}% | {status}")

        except Exception as e:
            results.append(f"处理 {info['name']} 时出错: {e}")

    # 生成报告
    report = f"--- 监控报告 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---\n"
    report += "\n".join(results) + "\n"
    print(report)

    # 保存到本地文件
    with open("monitor_report.txt", "a", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    print("开始检查自选股...")
    check_prices()
    print("检查完成。")