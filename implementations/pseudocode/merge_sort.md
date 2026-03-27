**no sentinal value, no multi allocations, single temp arr**

```
MergeSort(A, n)
    if A is null OR n < 2
        return

    create array temp[0 ... n-1]

    MergeSortHelper(A, temp, 0, n-1)


MergeSortHelper(A, temp, left, right)
    if left >= right
        return

    mid = left + (right - left) / 2

    MergeSortHelper(A, temp, left, mid)
    MergeSortHelper(A, temp, mid + 1, right)

    // Copy current segment into temp
    for i = left to right
        temp[i] = A[i]

    i = left
    j = mid + 1
    k = left

    // Merge back into A
    while i <= mid AND j <= right
        if temp[i] <= temp[j]
            A[k] = temp[i]
            i = i + 1
        else
            A[k] = temp[j]
            j = j + 1
        k = k + 1

    // Copy remaining elements from left half
    while i <= mid
        A[k] = temp[i]
        i = i + 1
        k = k + 1

    // Copy remaining elements from right half
    while j <= right
        A[k] = temp[j]
        j = j + 1
        k = k + 1

```