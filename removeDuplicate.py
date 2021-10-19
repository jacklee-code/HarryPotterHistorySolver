from main import ANSWERS_BOOK_FILENAME, RemoveAllPuncation
import collections

csv_filename = ANSWERS_BOOK_FILENAME

def main():
    writeNoRepeatCSV()

def writeNoRepeatCSV():
    dict = createOne2ManyDict()

    with open('No_Repeat.csv', mode='w', encoding='UTF-8') as writer:
        for key, value in dict.items():
            elements = value.split('||')
            if len(elements) > 1:
                for single in set(elements):
                    writer.write(f'{key};{single}\n')
            else:
                writer.write(f'{key};{value}\n')


def createOne2ManyDict():
    dict = {}
    with open(csv_filename, mode='r', encoding='UTF-8') as fr:
        for line in fr:
            pair = line.split(';')
            pure_key, pure_value = RemoveAllPuncation(pair[0]), RemoveAllPuncation(pair[1]).replace('\n', '')
            if len(pure_key) < 0:
                continue
            if pure_key in dict.keys():
                dict[pure_key] += '||' + pure_value
            else:
                dict[pure_key] = pure_value
    return dict

def checkDuplicate():
    dict = createOne2ManyDict()
    dupicateDict = {}
    for key, value in dict.items():

        s = '||'.join([item for item, count in collections.Counter(value.split('||')).items() if count > 1])
        if len(s) > 0:
            dupicateDict[key] = s
    return dupicateDict

if __name__ == '__main__':
    main()