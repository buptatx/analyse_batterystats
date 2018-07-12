#! -*-coding:utf-8 -*-

import json
import os
import xlwt
import time

def get_estimated_drain(filename):
    start_idx = 0
    end_idx = 0
    cur_idx = 0
    content = []
    target_proc = "target_proc"

    with open(filename, "rb") as mf:
        for sline in mf:
            line = str(sline).strip()
            if "proc=" in line and "com.borui.littlejane" in line:
                target_proc = line.split(':"')[0].split("proc=")[1]
            if "Over-counted" in line:
                end_idx = cur_idx
            if "Estimated power use" in line:
                start_idx = cur_idx

            content.append(line)
            cur_idx += 1

    if end_idx == 0:
        end_idx = start_idx + 30

    power_content = content[start_idx:end_idx+1]
    power_estimated = {}
    for line in power_content:
        if "Computed drain" in line:
            power_estimated["total_drain"] = int(line.split(", actual")[0].split("drain:")[1])
        elif "Screen:" in line:
            power_estimated["screen"] = float(line.split("Screen:")[1].split("\\")[0])
        elif target_proc in line:
            power_estimated["target"] = float(line.split(" ")[6])
        elif "Cell standby" in line:
            power_estimated["cell"] = float(line.split(" ")[6])
        elif "Wifi" in line:
            power_estimated["wifi"] = float(line.split(" ")[5])

    if "target" not in power_estimated:
        power_estimated["target"] = 0

    return power_estimated


def walk_data_dir(data_path):
    result = []
    for root, dirs, files in os.walk(data_path):
        for name in files:
            print(os.path.join(root, name))
            res = {}
            res = get_estimated_drain(os.path.join(root, name))
            if len(res) == 0:
                continue
            res["scene"] = name
            res["desc"] = get_scene_desc(name)
            result.append(res)

    result.sort(key=lambda x:(-x["target"], -x["total_drain"]))
    store_excel(result)


def get_scene_desc(name):
	if "no_internet_wpw_per_5_min" in name and "bgm" not in name:
		return "断网每5分钟播放一次唤醒词"
	elif "wifi_wpw_per_5_min" in name and "bgm" not in name:
		return "wifi每5分钟播放一次唤醒词"
	elif "4G_wpw_per_5_min" in name and "bgm" not in name:
		return "4G每5分钟播放一次唤醒词"
	elif "no_internet_wpw_per_5_min_with_bgm" in name:
		return "断网播放背景音乐每5分钟播放一次唤醒词"
	elif "wifi_wpw_per_5_min_with_bgm" in name:
		return "wifi播放背景音乐每5分钟播放一次唤醒词"
	elif "4G_wpw_per_5_min_with_bgm" in name:
		return "4G播放背景音乐每5分钟播放一次唤醒词"
	elif "4G_on_xj_view" in name:
		return "4G在小简页面静等待1小时"
	elif "wifi_on_xj_view" in name:
		return "wifi在小简页面静等待1小时"
	elif "no_internet_on_xj_view" in name:
		return "断网在小简页面静等待1小时"
	elif "4G_on_launcher_with_xj_app" in name:
		return "4G在原生桌面静等待1小时"
	elif "4G_without_xj_app" in name:
		return "4G未安装小简app"
	else:
		return "未知场景"


def store_excel(res):
    wbk = xlwt.Workbook()
    sht = wbk.add_sheet('estimated')
    data_size = xlwt.easyxf("font:height 280")

    sht.write(0, 0, "场景", data_size)
    sht.write(0, 1, "描述", data_size)
    sht.write(0, 2, "总消耗(mAh)", data_size)
    sht.write(0, 3, "屏幕消耗(mAh)", data_size)
    sht.write(0, 4, "小简消耗(mAh)", data_size)
    sht.write(0, 5, "移动网络(mAh)", data_size)
    sht.write(0, 6, "Wifi(mAh)", data_size)

    char_width = 269
    sht.col(0).width = char_width * 60
    sht.col(1).width = char_width * 50
    sht.col(2).width = char_width * 20
    sht.col(3).width = char_width * 20
    sht.col(4).width = char_width * 20
    sht.col(5).width = char_width * 20
    sht.col(6).width = char_width * 20

    cur_line = 1

    for item in res:
        if len(item) == 1:
            continue

        sht.write(cur_line, 0, item["scene"], data_size)
        sht.write(cur_line, 1, item["desc"], data_size)
        sht.write(cur_line, 2, item["total_drain"], data_size)
        sht.write(cur_line, 3, item["screen"], data_size)
        sht.write(cur_line, 4, item["target"], data_size)
        if "cell" in item:
            sht.write(cur_line, 5, item["cell"], data_size)
        else:
            sht.write(cur_line, 5, 0, data_size)
        if "wifi" in  item:
            sht.write(cur_line, 6, item["wifi"], data_size)
        else:
            sht.write(cur_line, 6, 0, data_size)

        cur_line += 1

    result_filename = time.strftime("result_%Y%m%d_%H%M%S.xlsx")
    wbk.save(result_filename)


if __name__ == "__main__":
    walk_data_dir("./data")