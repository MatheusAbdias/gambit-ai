from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Protocol, runtime_checkable


@runtime_checkable
class BaseComponent(Protocol):
    """Base protocol for all components."""


class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

    def __str__(self) -> str:
        return self.name.title()


class PieceColor(Enum):
    WHITE = 1
    BLACK = -1

    def __str__(self) -> str:
        return self.name.title()


class GameStatus(Enum):
    ACTIVE = "active"
    CHECK = "check"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"

    def __str__(self) -> str:
        return self.name.title()


@dataclass(frozen=True)
class Position(BaseComponent):
    x: int
    y: int

    def __str__(self) -> str:
        files = "abcdefgh"
        ranks = "87654321"
        return f"{files[self.x]}{ranks[self.y]}"


@dataclass
class Piece(BaseComponent):
    type: PieceType
    color: PieceColor
    has_moved: bool = False
    value: int = 1

    symbols: ClassVar[dict[tuple[PieceType, PieceColor], str]] = {
        (PieceType.PAWN, PieceColor.WHITE): "♙",
        (PieceType.KNIGHT, PieceColor.WHITE): "♘",
        (PieceType.BISHOP, PieceColor.WHITE): "♗",
        (PieceType.ROOK, PieceColor.WHITE): "♖",
        (PieceType.QUEEN, PieceColor.WHITE): "♕",
        (PieceType.KING, PieceColor.WHITE): "♔",
        (PieceType.PAWN, PieceColor.BLACK): "♟",
        (PieceType.KNIGHT, PieceColor.BLACK): "♞",
        (PieceType.BISHOP, PieceColor.BLACK): "♝",
        (PieceType.ROOK, PieceColor.BLACK): "♜",
        (PieceType.QUEEN, PieceColor.BLACK): "♛",
        (PieceType.KING, PieceColor.BLACK): "♚",
    }

    def __str__(self) -> str:
        return self.symbols.get((self.type, self.color), "?")

    def to_fen(self) -> str:
        """Convert to FEN notation (P, N, B, R, Q, K for white, lowercase for black)"""
        symbol = {
            PieceType.PAWN: "P",
            PieceType.KNIGHT: "N",
            PieceType.BISHOP: "B",
            PieceType.ROOK: "R",
            PieceType.QUEEN: "Q",
            PieceType.KING: "K",
        }[self.type]
        return symbol if self.color == PieceColor.WHITE else symbol.lower()


@dataclass
class Moveable(BaseComponent):
    valid_moves: list[tuple[int, int]] = field(default_factory=list)

    def __str__(self) -> str:
        moves = [Position(x, y).__str__() for x, y in self.valid_moves]
        return f"Valid moves: {', '.join(moves)}"


@dataclass
class Move(BaseComponent):
    """Represents a single move in the game."""

    from_pos: Position
    to_pos: Position
    piece: Piece
    captured_piece: Piece | None = None
    is_castling: bool = False
    is_en_passant: bool = False
    is_promotion: bool = False
    promotion_piece: PieceType | None = None

    def __str__(self) -> str:
        if self.is_castling:
            return "O-O" if self.to_pos.x > self.from_pos.x else "O-O-O"

        move_str = f"{self.piece.to_fen()}{self.from_pos}{self.to_pos}"
        if self.captured_piece:
            move_str += f"x{self.captured_piece.to_fen()}"
        if self.is_en_passant:
            move_str += "e.p."
        if self.is_promotion and self.promotion_piece:
            move_str += f"={self.promotion_piece}"
        return move_str


@dataclass
class GameState(BaseComponent):
    current_turn: PieceColor = PieceColor.WHITE
    status: GameStatus = GameStatus.ACTIVE
    castling_rights: list[int] = field(default_factory=lambda: [1, 1, 1, 1])
    en_passant_target: Position | None = None
    move_history: list[Move] = field(default_factory=list)
    halfmove_clock: int = 0
    fullmove_number: int = 1
    captured_pieces: list[Piece] = field(default_factory=list)
    check_positions: list[Position] = field(default_factory=list)
    pieces: dict[Position, Piece] = field(default_factory=dict)

    def __post_init__(self):
        if self.castling_rights is None:
            self.castling_rights = [1, 1, 1, 1]
        if self.move_history is None:
            self.move_history = []
        if self.captured_pieces is None:
            self.captured_pieces = []
        if self.check_positions is None:
            self.check_positions = []
        if self.pieces is None:
            self.pieces = {}

    def add_move(self, move: Move) -> None:
        self.move_history.append(move)

        if move.piece.type == PieceType.PAWN or move.captured_piece is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if move.piece.color == PieceColor.BLACK:
            self.fullmove_number += 1

        if move.captured_piece is not None:
            self.captured_pieces.append(move.captured_piece)

        self.current_turn = (
            PieceColor.BLACK
            if self.current_turn == PieceColor.WHITE
            else PieceColor.WHITE
        )

    def get_last_move(self) -> Move | None:
        return self.move_history[-1] if self.move_history else None

    def is_in_check(self) -> bool:
        return len(self.check_positions) > 0

    def can_castle(self, side: str) -> bool:
        if side == "K":
            return self.castling_rights[0] == 1
        if side == "Q":
            return self.castling_rights[1] == 1
        if side == "k":
            return self.castling_rights[2] == 1
        if side == "q":
            return self.castling_rights[3] == 1
        return False
