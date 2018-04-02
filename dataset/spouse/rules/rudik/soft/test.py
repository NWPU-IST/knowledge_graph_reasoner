def check_day(K, p, size_P, new_bucket):
    new_bucket[p] = 1
    if p + K + 1 <= size_P and new_bucket[p + K + 1] == 1:
        print "here"
        check = True
        for j in range(0,K):
            print p+j+1
            if new_bucket[p + j] == 1:
                check = False
                break
        print "now"
        if check:
            return check
    if p - K - 1 > 0 and new_bucket[p - K] == 1:
        print "here1"
        for k in xrange(0,K):
            print p -k
            if new_bucket[p - k] == 1:
                return False
        return True
    return False


def solutions(P, K):
    size_P = len(P)
    new_bucket = [None] * (size_P+1)
    i = 0
    for p in P:
        print p, new_bucket
        i += 1
        if check_day(K, p, size_P, new_bucket):
            return i
    return -1

print solutions([3,1,5,4,2],1)










# def solution(S, K):
#     # write your code in Python 3.6
#     # char_list = []
#     string = S.replace('-','')
#     formatted = ''
#     if len(string) <= K:
#         return string.upper()
#     while len(string) >= K:
#         new_chars = string[-K:]
#         print new_chars.upper()
#         if len(string) <= K:
#             formatted = new_chars.upper() + formatted
#         else:
#             formatted = '-'+new_chars.upper()+formatted
#         string = string[:-K]
#     # formatted = string.upper()+formatted
#     return formatted
#
# print solution("24-A0R-74K", 4)

# import itertools
# from operator import itemgetter
#
# def solutions(S):
#     data = []
#     hour, min = S.split(":")
#     print hour,min
#     digits = [s for s in S if s!=":"]
#     permu = list(set(itertools.permutations(digits)))
#     for per in permu:
#         if int(per[0]) < 3 and int(per[2])<5 and int(per[1])<5:
#             data.append(''.join(per))
#     if not data:
#         return S
#     sorted_data = sorted(data)
#     print sorted_data
#     time = hour+min
#     i = sorted_data.index(time)
#     print i
#     if i == len(sorted_data)-1:
#         return sorted_data[0][:2] + ":" + sorted_data[0][2:]
#     print sorted_data[i+1]
#     return sorted_data[i+1][:2]+":"+sorted_data[i+1][2:]
#
# print solutions("23:59")



