import re


def create6klist():
    list1 = []
    for i in range(31 + 1):
        tmplst = []
        list1.append(tmplst)
        for j in range(40 + 1):
            tmplst.append('*')
    return list1


def main():
    wordlist = create6klist()
    wordmean = create6klist()
    wordattr = create6klist()
    with open("6000.txt", encoding='utf-8') as f:
        raw = f.readlines()

    leftNum = -1
    rightNum = -1
    numSet = []
    lineNum = 1
    for line in raw:
        print("now in line ", lineNum)
        i = lineNum % 44
        if i == 1:
            numSet: list[int] = re.findall(r"(?<=测试)(\d+)(?=\t)", line)
            leftNum = int(numSet[0])
            if lineNum // 44 != 15:
                rightNum = int(numSet[1])
        elif 3 <= i <= 42:
            ln = leftNum - 1
            ii = i - 3
            content = re.findall(r"(?<=\S\t|\s\t)(\S+)", line)
            wordlist[ln][ii] = content[0]
            wordattr[ln][ii] = content[1]
            wordmean[ln][ii] = content[2]
            if lineNum // 44 != 15:
                rightNum = int(numSet[1])
                rn = rightNum - 1
                wordlist[rn][ii] = content[4]
                wordattr[rn][ii] = content[5]
                wordmean[rn][ii] = content[6]
        lineNum += 1

    # now print to new file
    with open("6000aux.txt", "w", encoding='utf-8') as f:
        n = 1
        for k in range(0, 31):
            for j in range(0, 40):
                if wordattr[k][j].startswith('"') and wordattr[k][j].endswith('"'):
                    wordattr[k][j] = wordattr[k][j][1:-1]
                if wordmean[k][j].startswith('"') and wordmean[k][j].endswith('"'):
                    wordmean[k][j] = wordmean[k][j][1:-1]
                final = str(n) + "|" + wordlist[k][j] + "|" + wordattr[k][j] + "|" + wordmean[k][j]
                f.write(final)
                f.write("\n")
                n += 1
    print("Completed!")


if __name__ == '__main__':
    main()
