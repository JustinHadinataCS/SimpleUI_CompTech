"""
Parser for SimpleUI Compiler
Parses tokens into Abstract Syntax Tree (AST)

PARSER PURPOSE:
The parser is the second stage of compilation after lexical analysis.
It takes the stream of tokens from the lexer and organizes them into a
hierarchical structure called an Abstract Syntax Tree (AST). The AST
represents the grammatical structure of the program.

PROCESS:
1. Uses grammar rules (from grammar.lark) to recognize valid syntax
2. Groups tokens into meaningful structures (shapes, properties)
3. Validates that code follows the language grammar
4. Transforms parse tree into custom AST nodes
5. Reports syntax errors for invalid code structure

The parser uses Lark library which handles the complex parsing logic,
but we provide a Transformer to convert Lark's parse tree into our
custom AST representation.
"""

from lark import Lark, Transformer
import ast_nodes

class SimpleUITransformer(Transformer):
    """
    Transforms Lark parse tree into custom AST nodes
    
    PURPOSE:
    This class converts Lark's generic parse tree into our custom AST structure.
    Lark parses according to grammar rules and produces a tree, but we need
    to transform it into our specific AST node types (Shape, Position, Color, etc.).
    
    HOW IT WORKS:
    - Lark calls methods named after grammar rules (e.g., "shape", "property")
    - Each method receives the parsed children as arguments
    - Methods extract values and construct appropriate AST nodes
    - The transformation happens automatically during parsing
    
    PROCESS:
    1. Terminal values (NUMBER, HEX, NAME) are converted to Python types
    2. Property rules (left_pos, width, etc.) are converted to tuples
    3. Shape rules collect all properties and create Shape AST nodes
    4. Start rule creates the root ShapeList containing all shapes
    """
    
    # Terminal transformations - convert token values to Python types
    def NUMBER(self, token):
        return float(token.value)
    
    def HEX(self, token):
        return ast_nodes.Color(token.value)
    
    def NAME(self, token):
        color_map = {
            'black': '#000000', 'white': '#FFFFFF',
            'red': '#FF0000', 'green': '#00FF00',
            'blue': '#0000FF', 'yellow': '#FFFF00',
            'cyan': '#00FFFF', 'magenta': '#FF00FF',
            'gray': '#808080', 'grey': '#808080',
        }
        return ast_nodes.Color(color_map.get(token.value.lower(), '#000000'))
    
    # Property transformations - convert property rules to (key, value) tuples
    # These tuples will be collected and used to build Shape objects
    def left_pos(self, args):
        """Extract left position value from 'NUMBER px left' pattern"""
        return ('left', args[0])
    
    def top_pos(self, args):
        """Extract top position value from 'NUMBER px top' pattern"""
        return ('top', args[0])
    
    def width(self, args):
        """Extract width value from 'w: NUMBER px' pattern"""
        return ('width', args[0])
    
    def height(self, args):
        """Extract height value from 'h: NUMBER px' pattern"""
        return ('height', args[0])
    
    def fill(self, args):
        """Extract fill color from 'fill: color' pattern"""
        return ('fill', args[0])
    
    def outside(self, args):
        """Extract outside/border color from 'outside: color' pattern"""
        return ('outside', args[0])
    
    def rounded(self, args):
        """Handle 'rounded' keyword - no value, just presence indicates True"""
        return ('rounded', True)
    
    def color(self, args):
        return args[0]
    
    def property(self, args):
        return args[0]
    
    # [FIX] Updated to handle the new Named Terminals from grammar
    def shape_name(self, args):
        if args:
            return args[0].value
        return None
    
    # Shape construction - main transformation logic
    def shape(self, args):
        """
        Transform a shape rule into a Shape AST node
        
        PURPOSE:
        This is the core transformation method. It takes all the properties
        parsed for a shape and constructs a complete Shape AST node.
        
        PROCESS:
        1. Initialize default property values (left=0, top=0, etc.)
        2. Extract shape name from last argument (e.g., "rectangle", "circle")
        3. Process all property tuples (left, top, width, height, fill, etc.)
        4. Apply defaults for missing properties
        5. Validate required properties (width and height must be present)
        6. Create and return Shape AST node with all properties
        
        Args:
            args: List containing property tuples and shape name
                 Example: [('left', 100), ('top', 50), ('width', 200), ..., 'rectangle']
        
        Returns:
            Shape AST node ready for code generation
        """
        if not args:
            raise ValueError("No arguments received for shape")
        
        # Initialize default property values
        # These will be overridden by actual properties found in the code
        props = {
            'left': 0.0, 'top': 0.0,  # Default position at origin
            'width': None, 'height': None,  # Must be provided
            'fill': None, 'outside': None,  # Optional colors
            'rounded': False  # Default to not rounded
        }
        
        # Last argument is the shape name (rectangle, circle, or line)
        shape_name = args[-1]
        
        # Process all property tuples (everything except the shape name)
        for prop in args[:-1]:
            if prop and isinstance(prop, tuple) and len(prop) == 2:
                key, value = prop
                props[key] = value  # Update property value
        
        # Validation: width and height are required for all shapes
        if props['width'] is None or props['height'] is None:
            raise ValueError("Width and height are required")
        
        # Construct Shape AST node with all properties
        return ast_nodes.Shape(
            shape_type=shape_name,
            position=ast_nodes.Position(props['left'], props['top']),
            size=ast_nodes.Size(props['width'], props['height']),
            fill_color=props['fill'] or ast_nodes.Color('#000000'),  # Default to black
            outside_color=props['outside'] or ast_nodes.Color('#000000'),  # Default to black
            rounded=props['rounded']
        )
    
    def start(self, args):
        return ast_nodes.ShapeList(shapes=args)


class Parser:
    """
    Parser class that uses Lark to parse SimpleUI source code
    
    PURPOSE:
    The Parser class initializes and manages the Lark parser engine.
    It loads the grammar specification and sets up the parsing pipeline.
    
    HOW IT WORKS:
    1. Loads grammar rules from grammar.lark file
    2. Initializes Lark parser with LALR algorithm (efficient parsing)
    3. Attaches transformer to convert parse tree to AST
    4. Provides parse() method to parse source code strings
    """
    
    def __init__(self, grammar_file: str = 'grammar.lark'):
        """
        Initialize the parser with grammar specification
        
        PURPOSE:
        Sets up the Lark parser engine by loading grammar rules and
        configuring the parsing algorithm and transformer.
        
        PROCESS:
        1. Read grammar file containing syntax rules
        2. Create Lark parser instance with:
           - LALR parser algorithm (efficient bottom-up parsing)
           - Start rule ('start' - the entry point of grammar)
           - Transformer (converts parse tree to our AST)
        3. Store parser for use in parse() method
        """
        try:
            # Load grammar specification from file
            with open(grammar_file, 'r', encoding='utf-8') as f:
                grammar = f.read()
            
            # Initialize Lark parser
            # LALR is an efficient parsing algorithm for context-free grammars
            self.parser = Lark(
                grammar,
                parser='lalr',  # LALR(1) parsing algorithm
                start='start',  # Entry point rule in grammar
                transformer=SimpleUITransformer()  # Converts parse tree to AST
            )
        except Exception as e:
            raise Exception(f"Failed to initialize parser: {e}")
    
    def parse(self, source_code: str) -> ast_nodes.ShapeList:
        """
        Parse source code into Abstract Syntax Tree
        
        PURPOSE:
        This is the main entry point for parsing. It takes SimpleUI source
        code and returns a complete AST representing the program structure.
        
        PROCESS:
        1. Lark tokenizes the source code (or uses our lexer tokens)
        2. Lark parses tokens according to grammar rules
        3. Transformer converts parse tree to AST nodes
        4. Returns root AST node (ShapeList) containing all shapes
        
        Args:
            source_code: SimpleUI source code as string
        
        Returns:
            ShapeList AST node containing all parsed shapes
        """
        return self.parser.parse(source_code)