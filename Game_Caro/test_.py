import turtle
import random
import this
import time

global move_history  # [(2,2),...]
global state
global board
global colors
global win
global screen
global type_play  # 1: máy , 0: người
global first  # 1: máy trước  , 0: người trước
global easy   #1 : easy 0: difficult

SIZE = 19


def make_empty_board(sz):
    board = []
    for i in range(sz):
        board.append([" "] * sz)
    return board


def is_empty(board):
    return board == [[' '] * len(board)] * len(board)


def is_in(board, y, x):
    return 0 <= y < len(board) and 0 <= x < len(board)


def is_win(board):
    x = score_of_col(board,
                     'x')  # {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, -1: {}}
    o = score_of_col(board, 'o')

    sum_sumcol_values(x)  # {0: 175, 1: 17, 2: 0, 3: 0, 4: 0, 5: {}, -1: {}}
    sum_sumcol_values(o)

    if 5 in x and x[5] >= 1:
        return 'x won'
    elif 5 in o and o[5] >= 1:
        return 'o won'

    if sum(x.values()) == x[-1] and sum(o.values()) == o[
        -1] or possible_moves(board) == []:
        return 'Draw'

    return 'Continue playing'


def getindexposition(x, y):
    '''
    lấy index
    '''
    intx, inty = int(x), int(y)

    dx, dy = x - intx, y - inty
    if dx > 0.5:
        x = intx + 1
    elif dx < -0.5:
        x = intx - 1
    else:
        x = intx
    if dy > 0.5:
        y = inty + 1
    elif dx < -0.5:
        y = inty - 1
    else:
        y = inty
    return x, y


##AI Engine

def march(board, y, x, dy, dx, length):
    '''
    tìm vị trí xa nhất trong dy,dx trong khoảng length
    '''
    yf = y + length * dy
    xf = x + length * dx
    # chừng nào yf,xf không có trong board
    while not is_in(board, yf, xf):
        yf -= dy
        xf -= dx

    return yf, xf


def score_ready(scorecol):
    '''
    Khởi tạo hệ thống điểm
    '''
    sumcol = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, -1: {}}
    for key in scorecol:
        for score in scorecol[key]:
            if key in sumcol[score]:
                sumcol[score][key] += 1
            else:
                sumcol[score][key] = 1

    return sumcol  # {0: {(0, 1): 56, (-1, 1): 34, (1, 0): 57, (1, 1): 33}, 1: {(0, 1): 4, (-1, 1): 2, (1, 0): 3, (1, 1): 3}, 2: {}, 3: {}, 4: {}, 5: {}, -1: {}}


def sum_sumcol_values(sumcol):
    """
     hợp nhất điểm của mỗi hướng
    :param sumcol:
    """

    for key in sumcol:
        if key == 5:
            sumcol[5] = int(len(sumcol[5]))
        else:
            sumcol[key] = sum(sumcol[key].values())


def score_of_list(lis, col):
    """
    :param lis: dãy 5 giá trị cần tính điểm
    :param col: 'x' hoặc 'o'
    :return: tổng số điểm của lis
    """
    blank = lis.count(' ')
    filled = lis.count(col)

    if blank + filled < 5:
        return -1
    elif blank == 5:
        return 0
    else:
        return filled


def row_to_list(board, y, x, dy, dx, yf, xf):
    """
    Trả về danh sách giá trị trong board từ (x,y) đến (xf. yf)
    :param board:   bàn cờ
    :param y:       y bắt đầu
    :param x:       x bắt đầu
    :param dy:      y tăng lên
    :param dx:      x tăng lên
    :param yf:      y kết thúc
    :param xf:      x kết thúc
    :return: row       [] danh sách điểm trong board từ (x,y) đến (xf, yf)
    """
    row = []
    while y != yf + dy or x != xf + dx:
        row.append(board[y][x])
        y += dy
        x += dx
    return row


def score_of_row(board, cordi, dy, dx, cordf, col):
    """
     trả về một list với mỗi phần tử đại diện cho số điểm của 5 khối
    :param board: bàn cờ
    :param cordi: (0,0) điểm bắt đầu
    :param dy:
    :param dx:
    :param cordf:   (0,9) điểm kết thúc
    :param col:     'x' hoặc 'o'
    :return: danh sách các điểm từ cordi đến cordf [0,1,2,5]
    """

    colscores = []
    y, x = cordi
    yf, xf = cordf
    row = row_to_list(board, y, x, dy, dx, yf, xf)
    for start in range(len(row) - 4):
        score = score_of_list(row[start:start + 5], col)
        colscores.append(score)

    return colscores


def score_of_col(board, col):
    '''
    tính toán điểm số mỗi hướng của column dùng cho is_win;
    '''

    f = len(board)
    # scores của 4 hướng đi
    scores = {(0, 1): [], (-1, 1): [], (1, 0): [], (1, 1): []}
    for start in range(len(board)):
        scores[(0, 1)].extend(
            score_of_row(board, (start, 0), 0, 1, (start, f - 1), col))
        scores[(1, 0)].extend(
            score_of_row(board, (0, start), 1, 0, (f - 1, start), col))
        scores[(1, 1)].extend(
            score_of_row(board, (start, 0), 1, 1, (f - 1, f - 1 - start), col))
        scores[(-1, 1)].extend(
            score_of_row(board, (start, 0), -1, 1, (0, start), col))

        if start + 1 < len(board):
            scores[(1, 1)].extend(score_of_row(board, (0, start + 1), 1, 1,
                                               (f - 2 - start, f - 1), col))
            scores[(-1, 1)].extend(
                score_of_row(board, (f - 1, start + 1), -1, 1,
                             (start + 1, f - 1), col))

    return score_ready(scores)


def score_of_col_one(board, col, y, x):
    '''
    trả lại điểm số của column trong y,x theo 4 hướng,
    key: điểm số khối đơn vị đó -> chỉ ktra 5 khối thay vì toàn bộ
    '''

    deepth = 2 if easy else 4

    scores = {(0, 1): [], (-1, 1): [], (1, 0): [], (1, 1): []}

    scores[(0, 1)].extend(
        score_of_row(board, march(board, y, x, 0, -1, 4), 0, 1,
                     march(board, y, x, 0, 1, deepth), col))

    scores[(1, 0)].extend(
        score_of_row(board, march(board, y, x, -1, 0, 4), 1, 0,
                     march(board, y, x, 1, 0, deepth), col))

    scores[(1, 1)].extend(
        score_of_row(board, march(board, y, x, -1, -1, 4), 1, 1,
                     march(board, y, x, 1, 1, deepth), col))

    scores[(-1, 1)].extend(
        score_of_row(board, march(board, y, x, -1, 1, 4), 1, -1,
                     march(board, y, x, 1, -1, deepth), col))

    return score_ready(scores)


def possible_moves(board):
    '''
    khởi tạo danh sách tọa độ có thể đi tại danh giới các nơi đã đánh phạm vi 4 đơn vị
    '''
    # mảng taken lưu giá trị của người chơi và của máy trên bàn cờ
    taken = []
    # mảng directions lưu hướng đi (8 hướng)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (-1, 1),
                  (1, -1)]
    # cord: lưu các vị trí không đi
    cord = {}

    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != ' ':
                taken.append((i, j))
    ''' duyệt trong hướng đi và mảng giá trị trên bàn cờ của người chơi và máy, kiểm tra nước không thể đi(trùng với
    nước đã có trên bàn cờ)
    '''
    for direction in directions:
        dy, dx = direction
        for coord in taken:
            y, x = coord
            for length in [1, 2, 3, 4]:
                move = march(board, y, x, dy, dx, length)
                if move not in taken and move not in cord:
                    cord[move] = False
    return cord


def TF34score(score3, score4):
    '''
    có 1 dãy 4 và 2 dãy 3 khác dãy 4 trở nên là chắc chắn win
    trả lại trường hợp chắc chắn có thể thắng(4 ô liên tiếp)
    '''
    for key4 in score4:
        if score4[key4] >= 1:
            for key3 in score3:
                if key3 != key4 and score3[key3] >= 2:
                    return True
    return False


def stupid_score(board, col, anticol, y, x):
    '''
    cố gắng di chuyển y,x
    trả về điểm số tượng trưng lợi thế
    '''

    global colors
    M = 1000
    res, adv, dis = 0, 0, 0

    # tấn công
    board[y][x] = col
    # draw_stone(x,y,colors[col])
    sumcol = score_of_col_one(board, col, y, x)
    a = winning_situation(sumcol)
    adv += a * M
    sum_sumcol_values(sumcol)  # {0: 0, 1: 15, 2: 0, 3: 0, 4: 0, 5: 0, -1: 0}
    adv += - sumcol[-1] + sumcol[1] + 4 * sumcol[2] + 8 * sumcol[3] + 16 * sumcol[
        4]

    # phòng thủ
    board[y][x] = anticol
    sumanticol = score_of_col_one(board, anticol, y, x)
    d = winning_situation(sumanticol)
    dis += d * (M - 100)
    sum_sumcol_values(sumanticol)
    dis += - sumanticol[-1] + sumanticol[1] + 4 * sumanticol[2] + 8 * sumanticol[
        3] + 16 * sumanticol[4]

    res = adv + dis

    board[y][x] = ' '
    return res


def winning_situation(sumcol):
    '''
    trả lại tình huống chiến thắng dạng như:
    {0: {},
    1: {(0, 1): 4, (-1, 1): 3, (1, 0): 4, (1, 1): 4},
    2: {},
    3: {},
    4: {},
    5: {},
    -1: {}}
    1-5 lưu điểm có độ nguy hiểm từ thấp đến cao,
    -1 là rơi vào trạng thái tồi, cần phòng thủ
    :return : 5 nếu tồn tại giá trị cho điểm 5
             4 it nhất 2 hàng 4 điểm
                có ít nhất 1 hàng 4 điểm và 2 hàng 3 điểm
            3 nếu có it nhất 4 hàng 3
            0
    '''

    if 1 in sumcol[5].values():
        return 5
    elif len(sumcol[4]) >= 2 or (
            len(sumcol[4]) >= 1 and max(sumcol[4].values()) >= 2):
        return 4
    elif TF34score(sumcol[3], sumcol[4]):
        return 4
    else:
        score3 = sorted(sumcol[3].values(), reverse=True)
        if len(score3) >= 2 and score3[0] >= score3[1] >= 2:
            return 3
    return 0


def best_move(board, col):
    '''
    trả lại điểm số của mảng trong lợi thế của từng màu
    :return: (a,b)
    '''
    if col == 'o':
        anticol = 'x'
    else:
        anticol = 'o'

    movecol = (0, 0)
    maxscorecol = ''
    # kiểm tra nếu bàn cờ rỗng thì cho vị trí random nếu không thì đưa ra giá trị trên bàn cờ nên đi
    if is_empty(board):
        movecol = (int((len(board)) * random.random()),
                   int((len(board[0])) * random.random()))
    else:
        moves = possible_moves(board)

        for move in moves:
            y, x = move
            if maxscorecol == '':
                scorecol = stupid_score(board, col, anticol, y, x)
                maxscorecol = scorecol
                movecol = move
            else:
                scorecol = stupid_score(board, col, anticol, y, x)
                if scorecol > maxscorecol:
                    maxscorecol = scorecol
                    movecol = move
    return movecol


def switchScreenWon(game_res):
    global win
    endGame(game_res)
    print(game_res)
    win = True


##Graphics Engine
##Event Click
def clickPvP(x, y):
    global board, colors, win, move_history, state, screen

    x, y = getindexposition(x, y)

    if x == -1 and y == -1 and len(move_history) != 0:
        x, y = move_history[-1]

        del (move_history[-1])
        board[y][x] = " "
        x, y = move_history[-1]

        del (move_history[-1])
        board[y][x] = " "
        return

    if not is_in(board, y, x):
        return

    if board[y][x] == ' ':
        if state == 'x':
            draw_stone(x, y, colors['x'])
            board[y][x] = 'x'
            state = 'o'
            move_history.append((x, y))

            game_res = is_win(board)
            if game_res in ["o won", "x won", "Draw"]:
                switchScreenWon(game_res)
                return

        elif state == 'o':
            draw_stone(x, y, colors['o'])
            board[y][x] = 'o'
            state = 'x'
            move_history.append((x, y))

            game_res = is_win(board)
            if game_res in ["o won", "x won", "Draw"]:
                switchScreenWon(game_res)
                return


def clickAI(x, y):
    global board, colors, win, move_history, first, state

    x, y = getindexposition(x, y)

    if x == -1 and y == -1 and len(move_history) != 0:
        x, y = move_history[-1]

        del (move_history[-1])
        board[y][x] = " "
        x, y = move_history[-1]

        del (move_history[-1])
        board[y][x] = " "
        return

    if not is_in(board, y, x):
        return

    if board[y][x] == ' ':
        draw_stone(x, y, colors[state])
        board[y][x] = state

        move_history.append((x, y))
        state = 'o' if state == 'x' else 'x'

        game_res = is_win(board)
        if game_res in ["o won", "x won", "Draw"]:
            switchScreenWon(game_res)
            return

        ay, ax = best_move(board, state)
        draw_stone(ax, ay, colors[state])
        board[ay][ax] = state

        move_history.append((ax, ay))
        state = 'x' if state == 'o' else 'o'
        game_res = is_win(board)
        if game_res in ["o won", "x won", "Draw"]:
            switchScreenWon(game_res)
            return


def buttonSelect(x, y):
    global type_play
    if (y > -20 and y < 50):
        if (x > -250 and x < -50):
            type_play = 0
            print("Chơi với người")
            screen.resetscreen()
            playGame()
        if (x > 50 and x < 250):
            type_play = 1
            print("Chơi với máy")
            screen.resetscreen()
            setting()


def buttonSelectSetting(x, y):
    global first
    if (y > -20 and y < 50):
        if (x > -250 and x < -50):
            first = 0
            print("Người đi trước")
            screen.resetscreen()
            selectDifficult()
        elif (x > 50 and x < 250):
            first = 1
            print("Máy đi trước")
            screen.resetscreen()
            selectDifficult()

def buttonSelectLevel(x, y):
    global easy
    if (y > -20 and y < 50):
        if (x > -250 and x < -50):
            easy = 0
            print("Khó")
            screen.resetscreen()
            playGame()
        if (x > 50 and x < 250):
            easy = 1
            print("Dễ")
            screen.resetscreen()
            playGame()

def clickRenew(x, y):
    if (y > 3.5 and y < 4):
        if (x > 6 and x < 8.4):
            print("Về trang chủ")
            screen.resetscreen()
            home()
        if (x > 10 and x < 12):
            print("Chơi lại")
            screen.resetscreen()
            playGame()


#
# init setting screen
#
def initialize():
    global win, board, screen, colors, move_history, state, type_play

    screen = turtle.Screen()
    screen.cv._rootwindow.resizable(False, False)
    screen.title("Caro")
    screen.setup(width=1000, height=1000)
    screen.tracer(200)
    # screen.mainloop()

    home()


def setColor():
    global win, board, screen, colors, move_history, state, type_play

    colors = {'o': turtle.Turtle(), 'x': turtle.Turtle(), 'w': turtle.Turtle(),
              'r': turtle.Turtle()}
    colors['o'].color('DarkBlue')
    colors['x'].color('Brown')
    colors['w'].color('white')
    colors['r'].color('red')
    colors['r'].width(3)

    for key in colors:
        colors[key].ht()
        colors[key].penup()
        colors[key].speed(0)


##
#   SCREEN
##
def home():
    global win, board, screen, colors, move_history, state, type_play
    screen.setworldcoordinates(-500, 500, 500, -500)
    screen.bgcolor('PeachPuff')
    screen.bgpic("background.gif")

    setColor()

    drawRectangle(-250, 50, 200, 70, colors['r'])
    drawRectangle(50, 50, 200, 70, colors['r'])
    drawText(-238, 25, "Chơi với người", 16, colors['r'])
    drawText(75, 25, "Chơi với máy", 16, colors['r'])

    turtle.onscreenclick(buttonSelect, 1)
    turtle.listen()
    turtle.done()


def setting():
    global colors, first
    setColor()

    drawRectangle(-250, 50, 200, 70, colors['r'])
    drawRectangle(50, 50, 200, 70, colors['r'])
    drawText(-238, 25, "Người đi trước", 16, colors['r'])
    drawText(75, 25, "Máy đi trước", 16, colors['r'])

    turtle.onscreenclick(buttonSelectSetting, 1)
    turtle.listen()
    turtle.done()

def selectDifficult():
    global colors, first, easy
    setColor()

    drawRectangle(-250, 50, 200, 70, colors['r'])
    drawRectangle(50, 50, 200, 70, colors['r'])
    drawText(-170, 25, "Khó", 16, colors['r'])
    drawText(130, 25, "Dễ", 16, colors['r'])

    turtle.onscreenclick(buttonSelectLevel, 1)
    turtle.listen()
    turtle.done()


def playGame():
    global win, board, screen, colors, move_history, state, type_play
    screen.bgpic("nopic")
    screen.setworldcoordinates(-1, SIZE, SIZE, -1)
    setColor()

    move_history = []
    win = False
    board = make_empty_board(SIZE)
    state = 'x'

    border = turtle.Turtle()
    border.speed(9)
    border.penup()

    side = SIZE / 2

    i = -1
    for start in range(SIZE + 1):
        border.goto(start - 0.5, side + side * i - 0.5)
        border.pendown()
        i *= -1
        border.goto(start - 0.5, side + side * i - 0.5)
        border.penup()

    i = 1
    for start in range(SIZE + 1):
        border.goto(side + side * i - 0.5, start - 0.5)
        border.pendown()
        i *= -1
        border.goto(side + side * i - 0.5, start - 0.5)
        border.penup()

    border.ht()
    if type_play:
        screen.onclick(clickAI)
        if first:
            ay, ax = best_move(board, 'x')
            draw_stone(ax, ay, colors['x'])
            board[ay][ax] = 'x'
            move_history.append((ax, ay))
            state = 'o'
    else:
        screen.onclick(clickPvP)

    screen.listen()
    screen.mainloop()


def endGame(winner):
    setColor()

    colors['w'].goto(4.5, 5)
    colors['w'].pendown()
    colors['w'].begin_fill()
    for i in range(2):
        colors['w'].forward(SIZE - 10)
        colors['w'].right(90)
        colors['w'].forward(4)
        colors['w'].right(90)
    colors['w'].end_fill()
    colors['w'].penup()

    drawText(8, 2.5, winner.upper(), 24, colors['r'])
    drawText(6, 4, "Trang chủ", 16, colors['r'])
    drawText(10, 4, "Chơi lại", 16, colors['r'])

    screen.onclick(clickRenew)
    turtle.listen()
    turtle.done()


##
#       PEN DRAW
##
def drawRectangle(x, y, width, height, pen):
    pen.goto(x, y)
    pen.pendown()

    for i in range(2):
        pen.forward(width)
        pen.right(90)
        pen.forward(height)
        pen.right(90)
    pen.penup()

    paint = turtle.Turtle()
    paint.penup()
    paint.goto(x, y)
    paint.pendown()
    paint.color("white")
    paint.begin_fill()

    for i in range(2):
        paint.forward(width)
        paint.right(90)
        paint.forward(height)
        paint.right(90)
    paint.end_fill()
    paint.penup()


def drawText(x, y, text, font, pen):
    pen.goto(x, y)
    pen.write(text, font=('Courier', font, 'bold'))


def draw_stone(x, y, colturtle):
    colturtle.width(15)
    colturtle.penup()
    if state == 'x':
        colturtle.goto(x - 0.3, y - 0.3)
        colturtle.pendown()
        colturtle.goto(x + 0.3, y + 0.3)
        colturtle.penup()
        colturtle.goto(x + 0.3, y - 0.3)
        colturtle.pendown()
        colturtle.goto(x - 0.3, y + 0.3)
    if state == 'o':

        # colturtle.begin_fill()
        colturtle.goto(x, y - 0.3)
        colturtle.pendown()
        colturtle.circle(0.3)
        # colturtle.end_fill()

    colturtle.penup()

if __name__ == '__main__':
    initialize()
