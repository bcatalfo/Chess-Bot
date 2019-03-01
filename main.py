import discord
import asyncio
from PIL import Image
import random

def add_piece(board_fname, piece_fnames, output_fname, x_coors, y_coors):
  assert (len(piece_fnames) == len(x_coors) == len(y_coors))
  num_pieces = len(piece_fnames)
  mimage = Image.open(board_fname).convert("RGBA")
  for i in range(0, num_pieces):
    limage = Image.open(piece_fnames[i]).convert("RGBA")
    # resize piece
    wsize = int(min(mimage.size[0], mimage.size[1]) * 1/8)
    wpercent = (wsize / float(limage.size[0]))
    hsize = int((float(limage.size[1]) * float(wpercent)))

    simage = limage.resize((wsize, hsize))
    mbox = mimage.getbbox()
    sbox = simage.getbbox()

    # put on the right x and y coor
    #print(len(mbox))
    #print(len(sbox))
    #print(mbox[2])
    box = (int((x_coors[i]*(mbox[2] - sbox[2])/(7))), int((7-y_coors[i]) * (mbox[3] - sbox[3])/(7)))
    mimage.paste(simage, box)
  mimage.save(output_fname, format="png")
#piece_fnames = ['knight.jpg', 'knight.jpg', 'knight.jpg', 'knight.jpg']
#x_coors = [1, 6, 1, 0]
#y_coors = [0, 5, 7, 0]
#add_piece('chess_board.png', piece_fnames, 'board_with_knight.png', x_coors, y_coors)

client = discord.Client()

class Game():
  #Represents a chess game being played
  games = []
  def __init__(self, game_type, players, difficulty):
    #game_type is a string to represent the type of the game(singleplayer, multiplayer, etc.), players is an array of Members who are playing the game, and difficulty is only used in singleplayer games to represent the ai difficulty
    if game_type == "singleplayer":
      print("We currently don't support a singleplayer mode.")
    elif game_type == "multiplayer":
      self.game_type = "multiplayer"
      if len(players) == 2:
        self.players = players
      else:
        print("Currently, all multiplayer games only support two players")
    self.board = Board()
    self.move_list = ""
    random.shuffle(players) # makes the order of the list random, so its random who's white or black
    self.players = players
    self.player_to_move = players[0] # white goes first
    Game.games.append(self)
  
  def move(self, pos1, pos2): # moves a piece from pos1 to pos2
    move_was_legal = False
    if self.is_legal(pos1, pos2):
      print("move was legal")
      self.board.get_tile(pos2).set_piece(self.board.get_tile(pos1).get_piece())
      self.board.get_tile(pos2).set_piece_color(self.board.get_tile(pos1).get_piece_color())
      self.board.get_tile(pos1).set_piece("Empty")
      self.board.get_tile(pos1).set_piece_color("")
      #print("b1: " + self.board.get_tile("b1").get_piece_color() + " " + self.board.get_tile("b1").get_piece())
      #print("c3: " + self.board.get_tile("c3").get_piece_color() + " " + self.board.get_tile("c3").get_piece())
      
      # switch turns
      if self.player_to_move == self.players[0]:
        self.player_to_move = self.players[1]
      else:
        self.player_to_move = self.players[0]
      
      move_was_legal = True
    else:
      print("move was illegal")
    #draw board
    self.board.draw()

    return move_was_legal
  
  def is_legal(self, pos1, pos2): # tells us if a player is allowed to make a move
    #pos1 and pos2 are just strings, we need to get their corresponding tiles
    tile1 = self.board.get_tile(pos1)
    tile2 = self.board.get_tile(pos2)
    #print(tile1.get_piece_color() + " " + self.color_to_move())
    if tile1.get_piece_color() != self.color_to_move(): # cant move someone else's pieces
      print(self.color_to_move())
      return False
    if tile2.get_piece_color() == self.color_to_move(): # can't capture your own piece
      print(tile2.get_piece_color(),self.color_to_move())
      return False
    if tile1.get_piece() == "Empty": # can't move an empty square
      return False
    # check all of the rules for all of the different pieces
    dist_x = abs(Board.letters.index(tile1.get_letter()) - Board.letters.index(tile2.get_letter()))
    print(dist_x)
    dist_y = abs(Board.numbers.index(tile1.get_number()) - Board.numbers.index(tile2.get_number()))
    print(dist_y)
    # Knight logic
    if tile1.get_piece() == "Knight" and ((dist_x > 2) or (dist_y > 2)):
      return False
    if tile1.get_piece() == "Knight" and ((dist_x == 0) or (dist_y == 0)):
      return False
    if tile1.get_piece() == "Knight" and ((dist_x == 2) and (dist_y != 1)):
      return False
    if tile1.get_piece() == "Knight" and ((dist_x == 1) and (dist_y != 2)):
      return False
    # Rook logic
    if tile1.get_piece() == "Rook" and (dist_x != 0 and dist_y != 0):
      # cant move diagonally
      return False
    # check all pieces inbetween tile1 and tile2 (cant hop over pieces)
    big_num = 0
    small_num = 0
    big_letter_index = 0
    small_letter_index = 0
    num1 = int(tile1.get_number())
    num2 = int(tile2.get_number())
    letter_index_1 = Board.letters.index(tile1.get_letter())
    letter_index_2 = Board.letters.index(tile2.get_letter())
    direction_x = 0
    direction_y = 0
    try:
      direction_y = (num2 - num1) / abs(num2 - num1)
    except ZeroDivisionError:
      print("No movement in the y direction")
    try:
      direction_x = (letter_index_2 - letter_index_1) / abs(letter_index_2 - letter_index_1)
    except ZeroDivisionError:
      print("No movement in the x direction")
    if num1 > num2:
      big_num = num1
      small_num = num2
    else:
      big_num = num2
      small_num = num1
    print("big num: " + str(big_num))
    print("small num: " + str(small_num))
    if letter_index_1 > letter_index_2:
      big_letter_index = letter_index_1
      small_letter_index = letter_index_2
    else:
      big_letter_index = letter_index_2
      small_letter_index = letter_index_1
    print("big letter index: " + str(big_letter_index))
    print("small letter index: " + str(small_letter_index))
    if tile1.get_piece() == "Rook":
      # check vertically if you are hopping over a piece
      for num in range(small_num + 1, big_num):
        pos = tile1.get_letter() + str(num)
        tile = self.board.get_tile(pos)
        print(pos + ": " + tile.get_piece())
        if tile.get_piece() != "Empty":
          return False
      # check horizontally if you are hopping over a piece
      for index in range(small_letter_index + 1, big_letter_index):
        pos = Board.letters[index] + tile1.get_number()
        tile = self.board.get_tile(pos)
        print(pos + ": " + tile.get_piece())
        if tile.get_piece() != "Empty":
          return False
    # Bishop logic
    if tile1.get_piece() == "Bishop" and (dist_x != dist_y):
      # Bishops move diagonally
      return False
    if tile1.get_piece() == "Bishop":
      # check diagonally if you are hopping over a piece
      print("direction_y: " + str(direction_y))
      print("direction_x: " + str(direction_x))
      for num in range(small_num + 1, big_num):
        pos = ""
        if direction_y > 0:
          pos = Board.letters[int(letter_index_1 + direction_x*(num - small_num))] + str(num)
        else:
          pos = Board.letters[int(letter_index_2 + -1*direction_x*(num - small_num))] + str(num)
        #try replacing direction_x with 1
        tile = self.board.get_tile(pos)
        print(pos + ": " + tile.get_piece())
        if tile.get_piece() != "Empty":
          return False
    # remember to eventually check if a move would leave you in check
    return True
    
  
  def color_to_move(self): # white if white is gonna move, black if black is gonna move
    if self.players.index(self.player_to_move) == 0:
      return "white"
    else:
      return "black"

class Board():
  #represents a chess board. basically an array of tiles
  initial_piece = {
    "a1" : "Rook", "b1" : "Knight", "c1" : "Bishop", "d1" : "Queen", "e1" : "King", "f1" : "Bishop", "g1" : "Knight", "h1" : "Rook",
    "a2" : "Pawn", "b2" : "Pawn", "c2" : "Pawn", "d2" : "Pawn", "e2" : "Pawn", "f2" : "Pawn", "g2" : "Pawn", "h2" : "Pawn",
    "a3" : "Empty", "b3" : "Empty", "c3" : "Empty", "d3" : "Empty", "e3" : "Empty", "f3" : "Empty", "g3" : "Empty", "h3" : "Empty",
    "a4" : "Empty", "b4" : "Empty", "c4" : "Empty", "d4" : "Empty", "e4" : "Empty", "f4" : "Empty", "g4" : "Empty", "h4" : "Empty",
    "a5" : "Empty", "b5" : "Empty", "c5" : "Empty", "d5" : "Empty", "e5" : "Empty", "f5" : "Empty", "g5" : "Empty", "h5" : "Empty",
    "a6" : "Empty", "b6" : "Empty", "c6" : "Empty", "d6" : "Empty", "e6" : "Empty", "f6" : "Empty", "g6" : "Empty", "h6" : "Empty",
    "a7" : "Pawn", "b7" : "Pawn", "c7" : "Pawn", "d7" : "Pawn", "e7" : "Pawn", "f7" : "Pawn", "g7" : "Pawn", "h7" : "Pawn",
    "a8" : "Rook", "b8" : "Knight", "c8" : "Bishop", "d8" : "Queen", "e8" : "King", "f8" : "Bishop", "g8" : "Knight", "h8" : "Rook"
  }
  letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
  numbers = ["1", "2", "3", "4", "5", "6", "7", "8"]
  colors = ["black", "white"]
  def __init__(self):
    self.tiles = []
    num = 0
    for letter in Board.letters:
      for number in Board.numbers:
        color = Board.colors[(Board.letters.index(letter) + num) % 2]
        piece_color = ""
        if number == "1" or number == "2":
          piece_color = "white"
        if number == "7" or number == "8":
          piece_color = "black"
        self.tiles.append(Tile(letter, number, Board.initial_piece[letter + number], piece_color, color))
        num += 1
  
  def get_tile(self, pos):
    for tile in self.tiles:
      if tile.get_name() == pos:
        return tile
    else:
      print("tile: " + pos + " does not exist")

  def draw(self):
    piece_fnames = []
    x_coors = []
    y_coors = []
    for tile in self.tiles:
      #Rook images
      if tile.piece == 'Rook' and tile.piece_color == 'black' and tile.color == "white":
        piece_fnames.append('Images/Rook/black_rook_white_background.png')
      elif tile.piece == 'Rook' and tile.piece_color == 'black' and tile.color == "black":
        piece_fnames.append('Images/Rook/black_rook_black_background.png')
      elif tile.piece == 'Rook' and tile.piece_color == 'white' and tile.color == "black":
        piece_fnames.append('Images/Rook/white_rook_black_background.png')
      elif tile.piece == 'Rook' and tile.piece_color == 'white' and tile.color == "white":
        piece_fnames.append('Images/Rook/white_rook_white_background.png')
      #Knight images
      elif tile.piece == 'Knight' and tile.piece_color == 'black' and tile.color == "white":
        piece_fnames.append('Images/Knight/black_knight_white_background.png')
      elif tile.piece == 'Knight' and tile.piece_color == 'black' and tile.color == "black":
        piece_fnames.append('Images/Knight/black_knight_black_background.png')
      elif tile.piece == 'Knight' and tile.piece_color == 'white' and tile.color == "black":
        piece_fnames.append('Images/Knight/white_knight_black_background.png')
      elif tile.piece == 'Knight' and tile.piece_color == 'white' and tile.color == "white":
        piece_fnames.append('Images/Knight/white_knight_white_background.png')
      #Bishop images
      elif tile.piece == 'Bishop' and tile.piece_color == 'black' and tile.color == "white":
        piece_fnames.append('Images/Bishop/black_bishop_white_background.png')
      elif tile.piece == 'Bishop' and tile.piece_color == 'black' and tile.color == "black":
        piece_fnames.append('Images/Bishop/black_bishop_black_background.png')
      elif tile.piece == 'Bishop' and tile.piece_color == 'white' and tile.color == "black":
        piece_fnames.append('Images/Bishop/white_bishop_black_background.png')
      elif tile.piece == 'Bishop' and tile.piece_color == 'white' and tile.color == "white":
        piece_fnames.append('Images/Bishop/white_bishop_white_background.png')
      #Queen images
      elif tile.piece == 'Queen' and tile.piece_color == 'black' and tile.color == "white":
        piece_fnames.append('Images/Queen/black_queen_white_background.png')
      elif tile.piece == 'Queen' and tile.piece_color == 'black' and tile.color == "black":
        piece_fnames.append('Images/Queen/black_queen_black_background.png')
      elif tile.piece == 'Queen' and tile.piece_color == 'white' and tile.color == "black":
        piece_fnames.append('Images/Queen/white_queen_black_background.png')
      elif tile.piece == 'Queen' and tile.piece_color == 'white' and tile.color == "white":
        piece_fnames.append('Images/Queen/white_queen_white_background.png')
      #King images
      elif tile.piece == 'King' and tile.piece_color == 'black' and tile.color == "white":
        piece_fnames.append('Images/King/black_king_white_background.png')
      elif tile.piece == 'King' and tile.piece_color == 'black' and tile.color == "black":
        piece_fnames.append('Images/King/black_king_black_background.png')
      elif tile.piece == 'King' and tile.piece_color == 'white' and tile.color == "black":
        piece_fnames.append('Images/King/white_king_black_background.png')
      elif tile.piece == 'King' and tile.piece_color == 'white' and tile.color == "white":
        piece_fnames.append('Images/King/white_king_white_background.png')
      #Pawn images
      elif tile.piece == 'Pawn' and tile.piece_color == 'black' and tile.color == "white":
        piece_fnames.append('Images/Pawn/black_pawn_white_background.png')
      elif tile.piece == 'Pawn' and tile.piece_color == 'black' and tile.color == "black":
        piece_fnames.append('Images/Pawn/black_pawn_black_background.png')
      elif tile.piece == 'Pawn' and tile.piece_color == 'white' and tile.color == "black":
        piece_fnames.append('Images/Pawn/white_pawn_black_background.png')
      elif tile.piece == 'Pawn' and tile.piece_color == 'white' and tile.color == "white":
        piece_fnames.append('Images/Pawn/white_pawn_white_background.png')
      else:
        continue
      x_coors.append(Board.letters.index(tile.letter))
      y_coors.append(Board.numbers.index(tile.number))
    add_piece('Images/chessboard.png', piece_fnames, 'board_with_pieces.png', x_coors, y_coors)

class Tile():
  #represents a tile on a chess board (includes info such as color, what piece is on it, algebraic notation, etc.)
  def __init__(self, letter, number, piece, piece_color, color):
    self.name = letter + number
    self.letter = letter
    self.number = number
    self.piece = piece
    self.piece_color = piece_color
    self.color = color
  
  def set_piece(self, piece):
    self.piece = piece
  
  def set_piece_color(self, piece_color):
    self.piece_color = piece_color
  
  def get_piece(self):
    return self.piece
  
  def get_piece_color(self):
    return self.piece_color
  
  def get_name(self):
    return self.name
  
  def get_color(self):
    return self.color
  
  def get_letter(self):
    return self.letter
  
  def get_number(self):
    return self.number

'''
user_input = ""
while user_input != "stop":
  print("You are moving for: " + Game.color_to_move())
  pos1 = input("What piece would you like to move? ")
  pos2 = input("Where would you like to move it? ")
  Game.move(pos1, pos2)

print("Can I move from b1 to c3?")
print(Game.is_legal("b1", "c3"))
print("Can I move from b1 to b3?")
print(Game.is_legal("b1", "b3"))
print("Can I move from b1 to b2?")
print(Game.is_legal("b1", "b2"))
print("Can I move from b1 to a3?")
print(Game.is_legal("b1", "a3"))
print("Can I move from b1 to d2?")
print(Game.is_legal("b1", "d2"))
print("Can I move from b8 to c6?")
print(Game.is_legal("b8", "c6"))
print(Game.player_to_move)
print("now it's black's turn")
Game.move("b8", "c6") #arbitrary move to switch turns
print("Can I move from b8 to c6?")
print(Game.is_legal("b8", "c6"))
print(Game.player_to_move)
print("Can I move from b1 to c3?")
print(Game.is_legal("b1", "c3"))
'''

game = Game("multiplayer", ["Ben", "Sam"], 0)
game.board.draw()

@client.event
async def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')
  for server in client.servers:
    for channel in server.channels:
      print(channel.name + ": " + str(channel.type))
      if str(channel.type) == 'text' and channel.name == 'bot-testing':
        print('Beep boop bot found testing channel')
        await client.send_message(channel, 'Chess Bot is here!')
        await client.send_file(channel, 'board_with_pieces.png')
  
@client.event
async def on_message(message):
  if message.content.startswith("!stop"):
    game = Game("multiplayer", ["Ben", "Sam"], 0)
    game.board.draw()
    await client.send_message(message.channel, "Game reset")
    await client.send_file(message.channel, 'board_with_pieces.png')
  if message.content.startswith("!move"):
    pos1 = message.content[6:8]
    pos2 = message.content[9:11]
    #await client.send_message(message.channel, "Moving " + pos1 + " to " + pos2 + ".")
    game = Game.games[-1] # last game in the list
    if game.move(pos1, pos2):
      await client.send_message(message.channel, "Moving " + pos1 + " to " + pos2 + ".")
    else:
      await client.send_message(message.channel, "Move was illegal.")
    game.board.draw()
    await client.send_file(message.channel, 'board_with_pieces.png')
  if message.content.startswith('!test'):
    counter = 0
    tmp = await client.send_message(message.channel, 'Calculating messages...')
    async for log in client.logs_from(message.channel, limit=100):
      if log.author == message.author:
        counter += 1
        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
  elif message.content.startswith('!sleep'):
    await asyncio.sleep(5)
    await client.send_message(message.channel, 'Done sleeping')

client.run('NTQ1Njg3NjQzNTYwNjA3NzQ0.D0dTsA.eJ-SkdNzcFiozDVBZrWqmEIM3zw')