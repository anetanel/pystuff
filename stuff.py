import random
from enum import Enum


class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)



def main():
    x = random.choice([i for i in Colors if i != Colors.WHITE])
    print(x)


if __name__ == '__main__':
    main()
