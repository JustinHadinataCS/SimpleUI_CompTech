"""
Custom Lexical Analyzer for SimpleUI Compiler
Tokenizes SimpleUI source code into meaningful tokens
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Enumeration of all token types in SimpleUI language"""
    # Literals
    NUMBER = "NUMBER"
    HEX_COLOR = "HEX_COLOR"
    COLOR_NAME = "COLOR_NAME"
    
    # Keywords
    PX = "PX"
    LEFT = "LEFT"
    TOP = "TOP"
    WIDTH = "WIDTH"
    HEIGHT = "HEIGHT"
    FILL = "FILL"
    OUTSIDE = "OUTSIDE"
    ROUNDED = "ROUNDED"
    
    # Shape types
    RECTANGLE = "RECTANGLE"
    CIRCLE = "CIRCLE"
    LINE = "LINE"
    
    # Punctuation
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    
    # Special
    EOF = "EOF"
    INVALID = "INVALID"


@dataclass
class Token:
    """Represents a single token with type, value, and position"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"


class LexerError(Exception):
    """Custom exception for lexical errors"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer Error at {line}:{column} - {message}")


class Lexer:
    """Custom hand-coded lexical analyzer"""
    
    # Keyword mappings
    KEYWORDS = {
        'px': TokenType.PX,
        'left': TokenType.LEFT,
        'top': TokenType.TOP,
        'w': TokenType.WIDTH,
        'h': TokenType.HEIGHT,
        'fill': TokenType.FILL,
        'outside': TokenType.OUTSIDE,
        'rounded': TokenType.ROUNDED,
        'rectangle': TokenType.RECTANGLE,
        'circle': TokenType.CIRCLE,
        'line': TokenType.LINE,
    }
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Get current character or None if at end"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Look ahead at character without consuming"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> Optional[str]:
        """Move to next character and return it"""
        char = self.current_char()
        if char:
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.current_char() and self.current_char() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        """Skip single-line comment starting with //"""
        if self.current_char() == '/' and self.peek_char() == '/':
            # Skip until end of line
            while self.current_char() and self.current_char() != '\n':
                self.advance()
            self.advance()  # Skip the newline
    
    def read_number(self) -> Token:
        """Read integer or float number"""
        start_line = self.line
        start_col = self.column
        num_str = ''
        
        # Read digits
        while self.current_char() and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()
        
        # Check for decimal point
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            num_str += self.current_char()
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                num_str += self.current_char()
                self.advance()
        
        return Token(TokenType.NUMBER, num_str, start_line, start_col)
    
    def read_hex_color(self) -> Token:
        """Read hexadecimal color #RRGGBB"""
        start_line = self.line
        start_col = self.column
        color_str = '#'
        self.advance()  # Skip #
        
        # Read exactly 6 hex digits
        hex_digits = 0
        while hex_digits < 6 and self.current_char() and self.current_char() in '0123456789ABCDEFabcdef':
            color_str += self.current_char()
            self.advance()
            hex_digits += 1
        
        if hex_digits != 6:
            raise LexerError(f"Invalid hex color '{color_str}' - expected 6 hex digits", start_line, start_col)
        
        return Token(TokenType.HEX_COLOR, color_str, start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read keyword or color name"""
        start_line = self.line
        start_col = self.column
        identifier = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            identifier += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        identifier_lower = identifier.lower()
        if identifier_lower in self.KEYWORDS:
            return Token(self.KEYWORDS[identifier_lower], identifier, start_line, start_col)
        
        # Otherwise, it's a color name
        return Token(TokenType.COLOR_NAME, identifier, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """Main tokenization method - converts source code to token list"""
        self.tokens = []
        
        while self.current_char():
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # Check for comment
            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            char = self.current_char()
            start_line = self.line
            start_col = self.column
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
            
            # Hex colors
            elif char == '#':
                self.tokens.append(self.read_hex_color())
            
            # Identifiers and keywords
            elif char.isalpha():
                self.tokens.append(self.read_identifier())
            
            # Punctuation
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, char, start_line, start_col))
                self.advance()
            
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, char, start_line, start_col))
                self.advance()
            
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, char, start_line, start_col))
                self.advance()
            
            else:
                raise LexerError(f"Unexpected character '{char}'", start_line, start_col)
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def get_tokens(self) -> List[Token]:
        """Get the list of tokens (for external access)"""
        return self.tokens


def tokenize_file(filepath: str) -> List[Token]:
    """Convenience function to tokenize a .sui file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    lexer = Lexer(source_code)
    return lexer.tokenize()


def tokenize_string(source_code: str) -> List[Token]:
    """Convenience function to tokenize a string"""
    lexer = Lexer(source_code)
    return lexer.tokenize()


# Example usage and testing
if __name__ == "__main__":
    # Test case 1: Basic rectangle
    test_code_1 = """
    100px left, 50px top, w:200px, h:100px, fill:#FF0000, outside:#000000, rounded, rectangle;
    """
    
    print("=== Test 1: Basic Rectangle ===")
    try:
        tokens = tokenize_string(test_code_1)
        for token in tokens:
            print(token)
    except LexerError as e:
        print(f"Error: {e}")
    
    print("\n=== Test 2: Multiple Shapes ===")
    test_code_2 = """
    // First shape
    w:100px, h:100px, circle;
    // Second shape overlapping
    50px left, 50px top, w:150px, h:75px, fill:#00FF00, rectangle;
    """
    
    try:
        tokens = tokenize_string(test_code_2)
        for token in tokens:
            print(token)
    except LexerError as e:
        print(f"Error: {e}")