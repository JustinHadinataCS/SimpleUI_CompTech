from lark import Lark, Transformer
import ast_nodes

class SimpleUITransformer(Transformer):
    """Transforms Lark parse tree into custom AST nodes"""
    
    # Terminals
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
    
    # Properties
    def left_pos(self, args):
        return ('left', args[0])
    
    def top_pos(self, args):
        return ('top', args[0])
    
    def width(self, args):
        return ('width', args[0])
    
    def height(self, args):
        return ('height', args[0])
    
    def fill(self, args):
        return ('fill', args[0])
    
    def outside(self, args):
        return ('outside', args[0])
    
    def rounded(self, args):
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
    
    # Shape construction
    def shape(self, args):
        if not args:
            raise ValueError("No arguments received for shape")
        
        props = {
            'left': 0.0, 'top': 0.0,
            'width': None, 'height': None,
            'fill': None, 'outside': None,
            'rounded': False
        }
        
        shape_name = args[-1]
        
        for prop in args[:-1]:
            if prop and isinstance(prop, tuple) and len(prop) == 2:
                key, value = prop
                props[key] = value
        
        # Validation
        if props['width'] is None or props['height'] is None:
            raise ValueError("Width and height are required")
        
        return ast_nodes.Shape(
            shape_type=shape_name,
            position=ast_nodes.Position(props['left'], props['top']),
            size=ast_nodes.Size(props['width'], props['height']),
            fill_color=props['fill'] or ast_nodes.Color('#000000'),
            outside_color=props['outside'] or ast_nodes.Color('#000000'),
            rounded=props['rounded']
        )
    
    def start(self, args):
        return ast_nodes.ShapeList(shapes=args)


class Parser:
    def __init__(self, grammar_file: str = 'grammar.lark'):
        try:
            with open(grammar_file, 'r', encoding='utf-8') as f:
                grammar = f.read()
            
            self.parser = Lark(
                grammar,
                parser='lalr',
                start='start',
                transformer=SimpleUITransformer()
            )
        except Exception as e:
            raise Exception(f"Failed to initialize parser: {e}")
    
    def parse(self, source_code: str) -> ast_nodes.ShapeList:
        return self.parser.parse(source_code)