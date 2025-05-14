from gambitai.ecs.components import (
    GameState,
    GameStatus,
    Move,
    Moveable,
    Piece,
    PieceColor,
    PieceType,
    Position,
)


def test_position():
    pos = Position(0, 0)
    assert pos.x == 0
    assert pos.y == 0
    assert str(pos) == "a8"

    pos = Position(7, 7)
    assert pos.x == 7
    assert pos.y == 7
    assert str(pos) == "h1"


def test_piece():
    pawn = Piece(PieceType.PAWN, PieceColor.WHITE)
    assert pawn.type == PieceType.PAWN
    assert pawn.color == PieceColor.WHITE
    assert not pawn.has_moved
    assert pawn.value == 1

    assert str(pawn) == "♙"
    assert str(Piece(PieceType.KING, PieceColor.BLACK)) == "♚"

    assert pawn.to_fen() == "P"
    assert Piece(PieceType.QUEEN, PieceColor.BLACK).to_fen() == "q"

    pawn.has_moved = True
    assert pawn.has_moved


def test_moveable():
    moveable = Moveable([(0, 0), (1, 1)])
    assert len(moveable.valid_moves) == 2
    assert (0, 0) in moveable.valid_moves
    assert (1, 1) in moveable.valid_moves

    assert "a8" in str(moveable)
    assert "b7" in str(moveable)


def test_move():
    from_pos = Position(0, 1)
    to_pos = Position(0, 2)
    piece = Piece(PieceType.PAWN, PieceColor.WHITE)
    move = Move(from_pos, to_pos, piece)

    assert move.from_pos == from_pos
    assert move.to_pos == to_pos
    assert move.piece == piece
    assert not move.is_castling
    assert not move.is_en_passant
    assert not move.is_promotion
    assert move.captured_piece is None

    captured = Piece(PieceType.PAWN, PieceColor.BLACK)
    capture_move = Move(from_pos, to_pos, piece, captured_piece=captured)
    assert capture_move.captured_piece == captured
    assert "x" in str(capture_move)

    castling_move = Move(
        Position(4, 0),
        Position(6, 0),
        Piece(PieceType.KING, PieceColor.WHITE),
        is_castling=True,
    )
    assert castling_move.is_castling
    assert str(castling_move) == "O-O"

    en_passant_move = Move(
        from_pos,
        to_pos,
        piece,
        is_en_passant=True,
        captured_piece=captured,
    )
    assert en_passant_move.is_en_passant
    assert "e.p." in str(en_passant_move)

    promotion_move = Move(
        from_pos,
        to_pos,
        piece,
        is_promotion=True,
        promotion_piece=PieceType.QUEEN,
    )
    assert promotion_move.is_promotion
    assert promotion_move.promotion_piece == PieceType.QUEEN
    assert "=Queen" in str(promotion_move)


def test_game_state():
    state = GameState()
    assert state.current_turn == PieceColor.WHITE
    assert state.status == GameStatus.ACTIVE
    assert state.castling_rights == [1, 1, 1, 1]
    assert state.en_passant_target is None
    assert len(state.move_history) == 0
    assert state.halfmove_clock == 0
    assert state.fullmove_number == 1
    assert len(state.captured_pieces) == 0
    assert len(state.check_positions) == 0
    assert len(state.pieces) == 0

    pawn_move = Move(
        Position(0, 1),
        Position(0, 2),
        Piece(PieceType.PAWN, PieceColor.WHITE),
    )
    state.add_move(pawn_move)
    assert len(state.move_history) == 1
    assert state.current_turn == PieceColor.BLACK
    assert state.get_last_move() == pawn_move
    assert state.halfmove_clock == 0
    assert state.fullmove_number == 1

    knight_move = Move(
        Position(1, 0),
        Position(2, 2),
        Piece(PieceType.KNIGHT, PieceColor.BLACK),
    )
    state.add_move(knight_move)
    assert state.halfmove_clock == 1
    assert state.fullmove_number == 2

    capture_move = Move(
        Position(2, 2),
        Position(3, 3),
        Piece(PieceType.KNIGHT, PieceColor.WHITE),
        captured_piece=Piece(PieceType.PAWN, PieceColor.BLACK),
    )
    state.add_move(capture_move)
    assert state.halfmove_clock == 0
    assert len(state.captured_pieces) == 1
    assert state.fullmove_number == 2

    assert not state.is_in_check()
    state.check_positions.append(Position(4, 0))
    assert state.is_in_check()

    assert state.can_castle("K")
    assert state.can_castle("Q")
    assert state.can_castle("k")
    assert state.can_castle("q")
    state.castling_rights = [0, 1, 1, 1]
    assert not state.can_castle("K")
    assert state.can_castle("Q")
