from game import Game
from config import check_and_install_packages


def main():
    # Check and install required packages
    check_and_install_packages()

    # Main game loop
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
