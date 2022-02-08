import time
from termcolor import colored

board = [' ' for x in range(10)]


def insertLetter(letter, pos):
    board[pos] = letter


def spaceIsFree(pos):
    return board[pos] == ' '


def printBoard(board):
    print('   |   |')
    print(' ' + board[1] + ' | ' + board[2] + ' | ' + board[3])
    print('   |   |')
    print('-----------')
    print('   |   |')
    print(' ' + board[4] + ' | ' + board[5] + ' | ' + board[6])
    print('   |   |')
    print('-----------')
    print('   |   |')
    print(' ' + board[7] + ' | ' + board[8] + ' | ' + board[9])
    print('   |   |')


def isWinner(bo, le):
    return ((bo[7] == le and bo[8] == le and bo[9] == le) or
            (bo[4] == le and bo[5] == le and bo[6] == le) or
            (bo[1] == le and bo[2] == le and bo[3] == le) or
            (bo[1] == le and bo[4] == le and bo[7] == le) or
            (bo[2] == le and bo[5] == le and bo[8] == le) or
            (bo[3] == le and bo[6] == le and bo[9] == le) or
            (bo[1] == le and bo[5] == le and bo[9] == le) or
            (bo[3] == le and bo[5] == le and bo[7] == le))


def playerMove():
    run = True
    while run:
        move = input("Please select a position to place an 'X' (1-9): ")
        try:  # Stops program from crashing of user doesn't enter a number between 1 and 9
            move = int(move)
            if 0 < move < 10:
                if spaceIsFree(move):
                    run = False
                    insertLetter('X', move)
                else:
                    print('Sorry, this space is occupied!')
            else:
                print('Please type a number within the range!')
        except:
            print('Please type a number!')


def compMove():
    possibleMoves = [x for x, letter in enumerate(board) if
                     letter == ' ' and x != 0]  # Checks for all the possible positions the comp can move into
    move = 0

    for let in ['O', 'X']:  # Gonna check to see if O's or X's will win
        for i in possibleMoves:
            boardCopy = board[:]  # Creating a copy for board
            boardCopy[i] = let
            if isWinner(boardCopy, let):
                move = i
                return move  # If player can win on next move the computer will block it

    cornersOpen = []
    for i in possibleMoves:
        if i in [1, 3, 5, 7, 9]:
            cornersOpen.append(i)
    if len(cornersOpen) > 0:
        move = selectRandom(cornersOpen)
        return move

    if 5 in possibleMoves:
        move = 5
        return move

    edgesOpen = []
    for i in possibleMoves:
        if i in [2, 4, 6, 8]:
            edgesOpen.append(i)
    if len(edgesOpen) > 0:
        move = selectRandom(edgesOpen)

    return move


def selectRandom(li):
    import random
    ln = len(li)
    r = random.randrange(0, ln)
    return li[r]


def isBoardFull(board):
    if board.count(' ') > 1:
        return False
    else:
        return True


def main():
    print("Welcome to Tic Tac Toe!")
    time.sleep(1)
    print("")
    printBoard(board)

    while not (isBoardFull(board)):
        if not (isWinner(board, 'O')):
            playerMove()
            printBoard(board)

        else:
            print(colored("Oh No you Have Lost!", 'red'))
            break

        if not (isWinner(board, 'X')):
            move = compMove()
            if move == 0:
                print('Tie Game')
            else:
                insertLetter('O', move)
                print("Computer placed an 'O' in position: ", move)
                printBoard(board)

        else:
            print(colored("Well done You Have Won!", 'green'))
            break

    if isBoardFull(board):
        print(colored('Tie Game!', 'blue'))


main()

while True:
    playAgain = input("Would You like To Play Again? y/n").upper()
    if playAgain == 'Y' or playAgain == 'YES':
        main()
    else:
        print("Goodbye!")
        break

