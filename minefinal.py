import random
from datetime import datetime
import sweeperlib
state = {
    "field": [],
    "hiden": [],
    "mine": [],
    "available": [],
    "visited": [],
    "tick": 0,
    "turn": 0,
    "flag": 0,
    "pressed": 0,
    "lose": False,
    "win": False
}

def reset():
    """reset the game index"""
    state['tick']=0
    state['pressed']=0
    state['lose']=False
    state['win']=False
    state['time']=datetime.now()
    state['turn']=0
    #pressed is the number of box have been opened
    state['pressed']=0
    #flag is the number of correct flaged mines
    state['flag']=0
    #visited to eliminate visit a visited box twice
    state['visited'] = [[False for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]


    state['field'] = []
    state['hiden']=[]
    state['available'] = []
    for row in range(FIELD_HEIGHT):
        state['field'].append([])
        state['hiden'].append([])
        for col in range(FIELD_WIDTH):
            state['field'][row].append(" ")
            state['hiden'][row].append(" ")
            state['available'].append((col, row))


def place_mines(fields,tiles,num):
    """
Places N mines to a field in random tiles.
"""
    state["mine"]=random.sample(tiles,num)
    for i in state["mine"]:
        pos_x, pos_y=i
        fields[pos_y][pos_x]="x"

def show_remainingmine(hiden,field):
    "show remaining mine"
    for i in state["mine"]:
        hiden[i[1]][i[0]]=field[i[1]][i[0]]

def addnummine(field):
    """Add number of nearby mine to the tile"""
    for ypos,rowf in enumerate(field):
        for xpos,colf in enumerate(rowf):
            if colf=="x":
                continue
            count=0

            for i in range(max(0, ypos - 1), min(FIELD_HEIGHT, ypos + 2)):
                for j in range(max(0, xpos - 1), min(FIELD_WIDTH, xpos + 2)):
                    if field[i][j]=='x':
                        count+=1
            field[ypos][xpos]=str(count)
            


def floodfill(posx,posy):
    """
Marks previously unknown connected areas as safe, starting from the given
x, y coordinates.
"""

    handling=[(posx,posy)]
    height = len(state['field'])
    width = len(state['field'][0])
    for sec in handling:
        state['visited'][sec[1]][sec[0]]="v"
        if state['field'][sec[1]][sec[0]]=="0":
            state['hiden'][sec[1]][sec[0]]=state['field'][sec[1]][sec[0]]
        else:
            break
        for i in range(max(0, sec[1] - 1), min(height, sec[1] + 2)):
            for j in range(max(0, sec[0] - 1), min(width, sec[0] + 2)):
                if state['visited'][i][j]:
                    continue
                state['visited'][i][j]="v"
                if state['field'][i][j]=="0":
                    handling.append((j,i))
                state['hiden'][i][j]=state['field'][i][j]
                state['pressed']+=1


def time_tick(time_unit):
    "game's time counting"
    if not state["lose"] and not state["win"]:
        state['tick'] += time_unit
    

def draw_field():
    """
A handler function that draws a field represented by a two-dimensional list
into a game window. This function is called whenever the game engine requests
a screen update.
"""
    
    sweeperlib.clear_window ()
    sweeperlib.draw_background ()
    sweeperlib.begin_sprite_draw ()
    for i,rows in enumerate(state["hiden"]):
        for j,cols in enumerate(rows):
            sweeperlib.prepare_sprite(cols, j * 40, i*40)
    sweeperlib.draw_sprites ()
    clock=f"{int(state['tick']/60):02}:{int(state['tick']-int(state['tick']/60)*60):02}"
    sweeperlib.draw_text(clock,5,FIELD_HEIGHT*40+2)
    if state["lose"]:
        sweeperlib.draw_text("lost",FIELD_WIDTH*40*2/3,FIELD_HEIGHT*40+2)
        if FIELD_WIDTH>14:
            alix=FIELD_WIDTH*40*1/5
            aliy=FIELD_HEIGHT*40+2
            sweeperlib.draw_text(f"|{MINENUM-state['flag']} mines left|",alix,aliy)
    if state["win"]:
        sweeperlib.draw_text("won",FIELD_WIDTH*40*2/3,FIELD_HEIGHT*40+2)


def handle_mouse(x_m,y_m,butt,mod):
    """
This function is called when a mouse button is clicked inside the game window.
Prints the position and clicked button of the mouse to the terminal.
"""
    if butt==sweeperlib.MOUSE_LEFT:
        ident="left mouse"
    elif butt==sweeperlib.MOUSE_MIDDLE:
        ident="middle mouse"
    elif butt==sweeperlib.MOUSE_RIGHT:
        ident="right mouse"
    tile_row=int(y_m/40)
    tile_col=int(x_m/40)
    if not state["lose"] and not state["win"]:
        if ident=="left mouse":
            if state['hiden'][tile_row][tile_col]==" ":
                state['pressed']+=1
                #print(pressed)
                state['turn']+=1
                state['hiden'][tile_row][tile_col]=state['field'][tile_row][tile_col]
                floodfill(tile_col,tile_row)
            if state['hiden'][tile_row][tile_col]=="x":
                if state["pressed"]==1:
                    state["field"] = []
                    for row in range(FIELD_HEIGHT):
                        state["field"].append([])
                        for _ in range(FIELD_WIDTH):
                            state["field"][row].append(" ")
                    state['available'].remove((tile_col, tile_row))
                    place_mines(state["field"],state['available'],MINENUM)
                    addnummine(state['field'])
                    state['hiden'][tile_row][tile_col]=state['field'][tile_row][tile_col]
                    #print((tile_col, tile_row))
                    #print(state['field'])
                    #print(state['hiden'])
                    floodfill(tile_col,tile_row)
                else:
                    state["lose"]=True
                    show_remainingmine(state['hiden'],state['field'])
                    with open("sweeper_record.txt",'a', encoding="utf-8") as record:
                        record.write(f"{state['time'].strftime('%Y-%m-%d %H:%M:%S')}    ")
                        record.write(f"You lost with {MINENUM-state['flag']}/{MINENUM} mines left ")
                        record.write(f"| played for {int(state['tick']/60):02}:")
                        record.write(f"{int(state['tick']-int(state['tick']/60)*60):02}")
                        record.write(f" minutes with {state['turn']} turns\n")
            elif state['pressed'] == FIELD_WIDTH*FIELD_HEIGHT-MINENUM:
                state["win"]=True
                with open("sweeper_record.txt",'a', encoding="utf-8") as record:
                    record.write(f"{state['time'].strftime('%Y-%m-%d %H:%M:%S')}    You won  ")
                    record.write(f"| played for {int(state['tick']/60):02}:")
                    record.write(f"{int(state['tick']-int(state['tick']/60)*60):02}")
                    record.write(f" minutes {state['turn']} turns\n")

        elif ident=="right mouse" and state['hiden'][tile_row][tile_col]==" ":
            state['hiden'][tile_row][tile_col]="f"
            if state['field'][tile_row][tile_col]=="x":
                state['flag']+=1
        elif ident=="right mouse" and state['hiden'][tile_row][tile_col]=="f":
            state['hiden'][tile_row][tile_col]=" "
            if state['field'][tile_row][tile_col]=="x":
                state['flag']-=1
    


def main():
    """
    Loads the game graphics, creates a game window and sets a draw handler for it.
    """
    
    sweeperlib.load_sprites(r"sprites")
    sweeperlib.create_window(FIELD_WIDTH*40, FIELD_HEIGHT*40+50,(124,216,255,255))
    sweeperlib.set_draw_handler(draw_field)
    sweeperlib.set_interval_handler(time_tick,1)
    sweeperlib.set_mouse_handler(handle_mouse)
    sweeperlib.start()


if __name__ == "__main__":
    print("Welcome to Minesweeper")

    while True:
        try:
            FIELD_WIDTH=int(input("enter field width: "))
            if FIELD_WIDTH <= 2:
                print("Try again, field width should be more than 2")
                continue
        except ValueError:
            print("Invalid number!")
        else:
            break

    while True:
        try:
            FIELD_HEIGHT=int(input("enter field height: "))
            if FIELD_HEIGHT <= 2:
                print("Try again, field height should be more than 2")
                continue
        except ValueError:
            print("Invalid number!")
        else:
            break

    while True:
        try:
            MINENUM=int(input("enter mine number: "))
            if MINENUM >= FIELD_HEIGHT*FIELD_WIDTH:
                print("Try again, mine num must be smaller than total tiles")
                continue
        except ValueError:
            print("Invalid number!")
        else:
            break

    """Prompt choice for user after game has initiated"""
    while True:
        print("what would you like to do")
        print("(1) New game") 
        print("(2) See score")
        print("(3) Quit")
        if state['tick']>0:
            print("(4) Continue?")
        choice=input("Choice: ")
        if choice=="1":  
            reset()
            place_mines(state["field"],state['available'],MINENUM)
            addnummine(state['field'])
            main()
        elif choice=="2":
            with open("sweeper_record.txt","r", encoding="utf-8") as file:
                for line in file.readlines():
                    print(line.strip())

        elif choice=="3":
            break
        elif choice=="4":
            main()
        else:
            print("Invalid choice")
