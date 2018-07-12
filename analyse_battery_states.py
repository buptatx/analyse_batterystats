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

    print("cur_idx: %d" % cur_idx)
    print("start_idx: %d" % start_idx)
    print("end_idx :%d" % end_idx)
    print("target_proc :%s" % target_proc)


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
            result.append(res)

    result.sort(key=lambda x:(-x["target"], -x["total_drain"]))
    store_excel(result)


def store_excel(res):
    wbk = xlwt.Workbook()
    sht = wbk.add_sheet('estimated')
    cur_line = 1

    for item in res:
        if len(item) == 1:
            continue

        sht.write(cur_line, 0, item["scene"])
        sht.write(cur_line, 1, item["total_drain"])
        sht.write(cur_line, 2, item["screen"])
        sht.write(cur_line, 3, item["target"])
        if "cell" in item:
            sht.write(cur_line, 4, item["cell"])
        else:
            sht.write(cur_line, 4, 0)
        if "wifi" in  item:
            sht.write(cur_line, 5, item["wifi"])
        else:
            sht.write(cur_line, 5, 0)

        cur_line += 1

    result_filename = time.strftime("result_%Y%m%d_%H%M%S.xlsx")
    wbk.save(result_filename)


if __name__ == "__main__":
    walk_data_dir("./data")
    #get_estimated_drain("./data/wifi_on_xj_view.txt")