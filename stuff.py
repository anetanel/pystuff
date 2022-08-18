def main():
    l1 = [1, 2, 3]
    l2 = [4, 5, 6, ]
    l1 = l2.copy()

    print(l2)
    print(l1)
    l1[0] = "x"

    print(l2)
    print(l1)


if __name__ == '__main__':
    main()
