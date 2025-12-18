"""
Custom Lexical Analyzer for SimpleUI Compiler
Tokenizes SimpleUI source code into meaningful tokens

LEXER PURPOSE:
The lexer (lexical analyzer) is the first stage of the compilation process.
It reads the raw source code character by character and groups them into 
meaningful "tokens" - the smallest units of the language (like keywords, 
numbers, colors, punctuation). This process is called "tokenization" or 
"lexical analysis".

PROCESS:
1. Reads source code character by character
2. Identifies patterns (numbers, keywords, colors, punctuation)
3. Groups characters into tokens with type and value
4. Handles whitespace and comments (skips them)
5. Reports errors for invalid characters
6. Returns a list of tokens for the parser to use

Example: "100px left" becomes:
  - Token(NUMBER, "100", line 1, col 1)
  - Token(PX, "px", line 1, col 4)
  - Token(LEFT, "left", line 1, col 7)
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
    """
    Custom hand-coded lexical analyzer
    
    PURPOSE:
    The Lexer class performs lexical analysis - converting raw source code
    into a stream of tokens. Each token represents a meaningful unit of the
    SimpleUI language (keywords, numbers, colors, punctuation marks).
    
    HOW IT WORKS:
    1. Initialization: Takes source code as input, sets up position tracking
    2. Character-by-character scanning: Reads each character sequentially
    3. Pattern recognition: Matches character sequences to token patterns
    4. Token creation: Creates Token objects with type, value, and position
    5. Error handling: Reports invalid characters or malformed tokens
    
    The lexer maintains position information (line, column) for error reporting.
    """
    
    # Keyword mappings - maps language keywords to their token types
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
        """
        Initialize the lexer with source code
        
        PURPOSE:
        Sets up the lexer's internal state for tokenization:
        - Stores the source code to analyze
        - Initializes position tracking (starts at beginning, line 1, column 1)
        - Prepares empty token list to collect results
        """
        self.source = source_code
        self.pos = 0  # Current character position in source code
        self.line = 1  # Current line number (for error reporting)
        self.column = 1  # Current column number (for error reporting)
        self.tokens: List[Token] = []  # List to store generated tokens
    
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
        """
        Main tokenization method - converts source code to token list
        
        PURPOSE:
        This is the core method of the lexer. It performs the complete
        lexical analysis process:
        1. Scans through source code character by character
        2. Skips whitespace and comments (they don't become tokens)
        3. Recognizes different token types based on starting character
        4. Delegates to specialized methods for complex tokens (numbers, colors, etc.)
        5. Creates simple tokens directly (punctuation)
        6. Handles errors for unexpected characters
        7. Adds EOF (End of File) token to mark completion
        
        PROCESS:
        - Loop through all characters in source code
        - For each character, determine what type of token it starts
        - Use pattern matching: digits -> number, '#' -> hex color, 
          letters -> keyword/identifier, punctuation -> punctuation token
        - Collect all tokens in order
        - Return complete token list for parser
        
        Returns:
            List of Token objects representing the entire source code
        """
        self.tokens = []
        
        # Main tokenization loop - process each character
        while self.current_char():
            # Skip whitespace (spaces, tabs, newlines) - they don't become tokens
            self.skip_whitespace()
            
            # If we've reached end after skipping whitespace, exit
            if not self.current_char():
                break
            
            # Check for comment (// ...) - skip entire comment line
            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # Save position for error reporting
            char = self.current_char()
            start_line = self.line
            start_col = self.column
            
            # Pattern matching: determine token type based on starting character
            
            # Numbers: start with a digit (0-9)
            if char.isdigit():
                self.tokens.append(self.read_number())
            
            # Hex colors: start with '#' symbol
            elif char == '#':
                self.tokens.append(self.read_hex_color())
            
            # Identifiers and keywords: start with a letter
            elif char.isalpha():
                self.tokens.append(self.read_identifier())
            
            # Punctuation tokens: single character tokens
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, char, start_line, start_col))
                self.advance()
            
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, char, start_line, start_col))
                self.advance()
            
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, char, start_line, start_col))
                self.advance()
            
            # Error: unexpected character that doesn't match any pattern
            else:
                raise LexerError(f"Unexpected character '{char}'", start_line, start_col)
        
        # Add EOF (End of File) token to mark end of token stream
        # This helps the parser know when to stop parsing
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