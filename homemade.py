"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.lichess_types import MOVE, HOMEMADE_ARGS_TYPE
import logging
import sys
import subprocess

# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


if sys.platform == "win32":
	stockfishPath = "stockfish\\stockfish.exe"
else:
	subprocess.call("chmod +x ./stockfish/stockfish")
	stockfishPath = "stockfish/stockfish"

class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

class BestFish(ExampleEngine):
    def __init__(self, *args, **kwargs):
        self.stockfish = chess.engine.SimpleEngine.popen_uci(stockfishPath)
        super().__init__(*args, **kwargs)

    def evaluate(self, board, timeLimit=0.1):
        return self.stockfish.analyse(board, chess.engine.Limit(time=timeLimit - 0.01))["score"].relative

    def search(self, board: chess.Board, timeLeft, *args):
        searchTime = timeLeft
        if isinstance(searchTime, chess.engine.Limit) and searchTime.time is not None:
            searchTime = searchTime.time / 1000
        else:
            searchTime = 0.1 
        move = self.stockfish.play(board, chess.engine.Limit(time=searchTime)).move
        return PlayResult(move, None)

class WorstFish(ExampleEngine):

	def __init__ (self, *args, **kwargs):
		self.stockfish = chess.engine.SimpleEngine.popen_uci(stockfishPath)
		super().__init__(*args, **kwargs)

	def evaluate (self, board, timeLimit = 0.1):
		result = self.stockfish.analyse(board, chess.engine.Limit(time = timeLimit - 0.01))
		return result["score"].relative

	def search (self, board: chess.Board, timeLeft, *args):
		# Get amount of legal moves
		legalMoves = tuple(board.legal_moves)

		# Base search time per move in seconds
		searchTime = 0.1

		# If the engine will search for more than 10% of the remaining time, then shorten it
		# to be 10% of the remaining time
		# Also, dont do this on the first move (because of weird behaviour with timeLeft being a Limit on first move)
		if type(timeLeft) != chess.engine.Limit:
			timeLeft /= 1000  # Convert to seconds
			if len(legalMoves) * searchTime > timeLeft / 10:
				searchTime = (timeLeft / 10) / len(legalMoves)

		# Initialise variables
		worstEvaluation = None
		worstMoves = []

		# Evaluate each move
		for move in legalMoves:
			# Record if the move is a capture
			move.isCapture = board.is_capture(move)

			# Play move
			board.push(move)

			# Record if the move is a check
			move.isCheck = board.is_check()

			# Evaluate position from opponent's perspective
			evaluation = self.evaluate(board, searchTime)

			# If the evaluation is better than worstEvaluation, replace the worstMoves list with just this move
			if worstEvaluation is None or worstEvaluation < evaluation:
				worstEvaluation = evaluation
				worstMoves = [move]

			# If the evaluation is the same as worstEvaluation, append the move to worstMoves
			elif worstEvaluation == evaluation:
				worstMoves.append(move)

			# Un-play the move, ready for the next loop
			board.pop()

		# Categorise the moves into captures, checks, and neither
		worstCaptures = []
		worstChecks = []
		worstOther = []

		for move in worstMoves:
			if move.isCapture:
				worstCaptures.append(move)
			elif move.isCheck:
				worstChecks.append(move)
			else:
				worstOther.append(move)

		# Play a random move, preferring moves first from Other, then from Checks, then from Captures
		if len(worstOther) != 0:
			return PlayResult(random.choice(worstOther), None)
		elif len(worstChecks) != 0:
			return PlayResult(random.choice(worstChecks), None)
		else:
			return PlayResult(random.choice(worstCaptures), None)

	def quit(self):
		self.stockfish.close()


global chance_worst
chance_worst = 7

class MediumFish(ExampleEngine):
	def __init__(self, *args, **kwargs):
		self.stockfish = chess.engine.SimpleEngine.popen_uci(stockfishPath)
		super().__init__(*args, **kwargs)

	def set_worst_move_percent(self, percent):
		global chance_worst
		chance_worst = percent
	def evaluate(self, board, timeLimit=0.1):
		return self.stockfish.analyse(board, chess.engine.Limit(time=timeLimit - 0.01))["score"].relative

	def search(self, board: chess.Board, timeLeft, *args):
		# chance_worst = 50
		global chance_worst
		if random.random() * 100 < chance_worst:
			# WorstFish
			print("WorstFish")
			
			# Get amount of legal moves
			legalMoves = tuple(board.legal_moves)

			# Base search time per move in seconds
			searchTime = 0.1

			# If the engine will search for more than 10% of the remaining time, then shorten it
			# to be 10% of the remaining time
			# Also, dont do this on the first move (because of weird behaviour with timeLeft being a Limit on first move)
			if type(timeLeft) != chess.engine.Limit:
				timeLeft /= 1000  # Convert to seconds
				if len(legalMoves) * searchTime > timeLeft / 10:
					searchTime = (timeLeft / 10) / len(legalMoves)

			# Initialise variables
			worstEvaluation = None
			worstMoves = []

			# Evaluate each move
			for move in legalMoves:
				# Record if the move is a capture
				move.isCapture = board.is_capture(move)

				# Play move
				board.push(move)

				# Record if the move is a check
				move.isCheck = board.is_check()

				# Evaluate position from opponent's perspective
				evaluation = self.evaluate(board, searchTime)

				# If the evaluation is better than worstEvaluation, replace the worstMoves list with just this move
				if worstEvaluation is None or worstEvaluation < evaluation:
					worstEvaluation = evaluation
					worstMoves = [move]

				# If the evaluation is the same as worstEvaluation, append the move to worstMoves
				elif worstEvaluation == evaluation:
					worstMoves.append(move)

				# Un-play the move, ready for the next loop
				board.pop()

			# Categorise the moves into captures, checks, and neither
			worstCaptures = []
			worstChecks = []
			worstOther = []

			for move in worstMoves:
				if move.isCapture:
					worstCaptures.append(move)
				elif move.isCheck:
					worstChecks.append(move)
				else:
					worstOther.append(move)

			# Play a random move, preferring moves first from Other, then from Checks, then from Captures
			if len(worstOther) != 0:
				return PlayResult(random.choice(worstOther), None)
			elif len(worstChecks) != 0:
				return PlayResult(random.choice(worstChecks), None)
			else:
				return PlayResult(random.choice(worstCaptures), None)
		else:
			# StockFish
			print("Stockfish")
			searchTime = timeLeft
			if isinstance(searchTime, chess.engine.Limit) and searchTime.time is not None:
				searchTime = searchTime.time / 400
			else:
				searchTime = 1 
			move = self.stockfish.play(board, chess.engine.Limit(time=searchTime)).move
			return PlayResult(move, None)

	def quit(self):
		self.stockfish.close()