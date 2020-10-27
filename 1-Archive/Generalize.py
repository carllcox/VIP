file = 'extraneousWords.txt'

def generalize(file, hypo):
    f = open(file, 'r')
    text = f.read().strip().split()

    hypList = hypo.split(" ")
    for i in range(len(hypList)):
        for item in hypList:
            if item in text:
                hypList[hypList.index(item)] = ''

    s = ''
    for i in hypList:
        if i != '':
            s += i + ','

    return s[:-1]
