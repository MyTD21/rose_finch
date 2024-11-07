import argparse
import logging
import math
import json
import re
#import lhotse

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--job",
        type=str,
        help="get_train_data, get_test_data, verify_test",
        required=True,
    )

    parser.add_argument(
        "--input",
        type=str,
        default="input",
        help="input file",
    )

    parser.add_argument(
        "--input_test_list",
        type=str,
        default="input",
        help="input file",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="rosefinch_output",
        help="output file",
    )

    parser.add_argument(
        "--train-jsonfile",
        type=str,
        default="llm_asr_result",
        help="json file for llm training",
    )


    return parser


def verify_test(args):

    with open(args.input_test_list, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file]
   
    result_len = 0
    for item in lines:
        file_name = "/apdcephfs_cq10/share_1603164/user/yiwenyshao/icefall/egs/tencent/ASR/data/fbank_deduplicate/" + item
        cut = lhotse.CutSet.from_file(file_name)
        result_len += len(cut)
        print(item, len(cut))

    print(result_len)
    return

    with open(args.input_file, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file]
    for item in lines:
        with open(item, 'r', encoding='utf-8') as file:
            lines1 = [line.strip() for line in file]

        print(item, len(lines1))


def qw_fix(args):
    with open(args.input, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file]

    lines_fixed = []
    for item in lines:
        if  'hyp=' in item:
            position = item.find('<')
            if position != -1:
                item = item[:position - 3]
                item += ']'
        lines_fixed.append(item)
        

    with open(args.output, "w+", encoding='utf-8') as file:
        for item in lines_fixed:
            file.write(item+"\n")

def qw_fix_ori(args):
    with open(args.input, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file]

    lines_oper = []
    lines_oper2 = []
    for item in lines:
        splits = item.split(' ref ')
        rec =  splits[0].split(' f ')[0]
        fixed = splits[0].split(' f ')[1]
        lab = splits[1]
       
        fixed = fixed.split("</s>")[0]
        lines_oper.append((rec, fixed, lab))
        lines_oper2.append(f"{rec} f {fixed} ref {lab}\n")

#    with open(args.output + "cmp_fixed", "w", encoding='utf-8') as file:
#        for index, item in enumerate(lines_oper):
#            ref = list("".join(item[2]))
#            hyp = list("".join(item[1]))
#            file.write(f"{hyp}\tref={ref}\n")
#
#    with open(args.output + "cmp_ori", "w", encoding='utf-8') as file:
#        for index, item in enumerate(lines_oper):
#            ref = list("".join(item[2]))
#            hyp = list("".join(item[0]))
#            file.write(f"{hyp}\tref={ref}\n")

    with open(args.output, "w+", encoding='utf-8') as file:
        for item in lines_oper2:
            file.write(item)


def find_differences(str1, str2):
    # 将字符串转换为集合，以便找到独特的字符
    set1 = set(str1)
    set2 = set(str2)

    # 找出只在第一个字符串中的字符
    diff1 = set1 - set2
    # 找出只在第二个字符串中的字符
    diff2 = set2 - set1

    # 将差异转换为列表并排序（可选，为了输出有序的差异）
    diff_list = sorted(list(diff1)) + sorted(list(diff2))

    # 将差异列表转换为字符串，每个差异字符之间用逗号分隔
    diff_string = ', '.join(diff_list)

    return diff_string

def all_chars_in_string(chars, str1):
    str_set = set(str1)
    for item in chars:
        if item in str1:
            return True
    return False

def cmp_txt(args):
    with open(args.input, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file]

    lines_ori = []
    lines_fixed = []
    for item in lines:
        splits = item.split(' ')
        lines_ori.append((splits[1], splits[5]))
        lines_fixed.append((splits[3], splits[5]))


    with open(args.output + "cmp_fixed", "w", encoding='utf-8') as file:
        for index, item in enumerate(lines_fixed):
            file.write(f"{item[0]}\tref={item[1]}\n")
    with open(args.output + "cmp_ori", "w", encoding='utf-8') as file:
        for index, item in enumerate(lines_ori):
            file.write(f"{item[0]}\tref={item[1]}\n")
#


#
#    with open(args.output + "cmp_ori", "w", encoding='utf-8') as file:
#        for index, item in enumerate(lines_oper):
#            ref = list("".join(item[2]))
#            hyp = list("".join(item[0]))
#            file.write(f"{hyp}\tref={ref}\n")


def fix_ta(args):
    with open(args.input, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file]
   
    ta = '他她它'

    lines_oper = []
    for item in lines:
        splits = item.split(' ')
        #lines_oper.append((splits[1], splits[3], splits[5]))
        if splits[1] != splits[3] :
            diffs = find_differences(splits[1],splits[3])
            if all_chars_in_string(diffs.split(','), ta):
                lines_oper.append((splits[1], splits[1], splits[5]))
            else:
                lines_oper.append((splits[1], splits[3], splits[5]))
        else:
            lines_oper.append((splits[1], splits[3], splits[5]))

            #diffs = find_differences(splits[1],splits[3])
            #ret = all_chars_in_string(diffs.split(','), ta)
            #import pdb; pdb.set_trace()
            #print("diff ", splits[1], splits[3], find_differences(splits[1],splits[3]))

    result_file = args.output

    with open(result_file + "_benchmark", "w", encoding='utf-8') as file:
        for index, item in enumerate(lines_oper):
            ref = list("".join(item[2]))
            hyp = list("".join(item[0]))
            file.write(f"{index}:\tref={ref}\n")
            file.write(f"{index}:\thyp={hyp}\n")

    with open(result_file + "_fixed", "w", encoding='utf-8') as file:
        for index, item in enumerate(lines_oper):
            ref = list("".join(item[2]))
            hyp = list("".join(item[1]))
            file.write(f"{index}:\tref={ref}\n")
            file.write(f"{index}:\thyp={hyp}\n")

    with open(args.output + "_cmp_fixed", "w", encoding='utf-8') as file:
        for index, item in enumerate(lines_oper):
            file.write(f"{item[1]}\tref={item[2]}\n")
    with open(args.output + "_cmp_ori", "w", encoding='utf-8') as file:
        for index, item in enumerate(lines_oper):
            file.write(f"{item[0]}\tref={item[2]}\n")


def main():
    logging.info("")
    parser = get_parser()
    args = parser.parse_args()

    print(args)

    if args.job == "verify_test":
        verify_test(args)
    elif args.job == "qw_fix":
        qw_fix(args)
    elif args.job == "fix_ta":
        fix_ta(args)
    elif args.job == "qw_fix_ori":
        qw_fix_ori(args)
    elif args.job == "cmp":
        cmp_txt(args)
    else:
        print("err job index")
    

if __name__ == "__main__":
    main()
