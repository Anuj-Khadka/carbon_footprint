N = 1_000_000

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    L = merge_sort(arr[:mid])
    R = merge_sort(arr[mid:])
    i = j = 0
    result = []
    while i < len(L) and j < len(R):
        if L[i] <= R[j]: result.append(L[i]); i += 1
        else:             result.append(R[j]); j += 1
    result.extend(L[i:])
    result.extend(R[j:])
    return result

arr = list(range(N, 0, -1))
sorted_arr = merge_sort(arr)
print(sorted_arr[-1])
