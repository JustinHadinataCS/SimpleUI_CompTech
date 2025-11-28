"""
AST Node Definitions for SimpleUI Compiler
Represents the abstract syntax tree structure after parsing
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Position:
    """Represents x, y coordinates for shape placement"""
    x: float = 0.0  # left position (default 0)
    y: float = 0.0  # top position (default 0)
    
    def __repr__(self):
        return f"Position(x={self.x}, y={self.y})"


@dataclass
class Size:
    """Represents width and height dimensions"""
    width: float
    height: float
    
    def __repr__(self):
        return f"Size(w={self.width}, h={self.height})"


@dataclass
class Color:
    """Represents color in hex format"""
    hex_value: str  # e.g., "#FF0000" or "#000000"
    
    def __post_init__(self):
        # Normalize hex color to uppercase with #
        if not self.hex_value.startswith('#'):
            self.hex_value = f"#{self.hex_value}"
        self.hex_value = self.hex_value.upper()
    
    def __repr__(self):
        return f"Color({self.hex_value})"


@dataclass
class Shape:
    """Base representation of a drawable shape"""
    shape_type: str  # "rectangle", "circle", or "line"
    position: Position
    size: Size
    fill_color: Color
    outside_color: Color  # border/outline color
    rounded: bool = False
    
    def __repr__(self):
        return (f"Shape(type={self.shape_type}, pos={self.position}, "
                f"size={self.size}, fill={self.fill_color}, "
                f"outside={self.outside_color}, rounded={self.rounded})")


@dataclass
class ShapeList:
    """Root AST node containing all shapes in drawing order"""
    shapes: List[Shape]
    
    def __repr__(self):
        return f"ShapeList(count={len(self.shapes)})"
    
    def __iter__(self):
        """Allow iteration over shapes"""
        return iter(self.shapes)


# Helper functions for AST construction

def create_default_position() -> Position:
    """Create default position at origin (0, 0)"""
    return Position(0.0, 0.0)


def create_default_color() -> Color:
    """Create default black color"""
    return Color("#000000")


def create_shape(shape_type: str, 
                properties: dict,
                size: Size) -> Shape:
    """
    Factory function to create a Shape with proper defaults
    
    Args:
        shape_type: "rectangle", "circle", or "line"
        properties: dict with optional keys: position, fill, outside, rounded
        size: Size object (required)
    
    Returns:
        Shape object with all required fields
    """
    return Shape(
        shape_type=shape_type,
        position=properties.get('position', create_default_position()),
        size=size,
        fill_color=properties.get('fill', create_default_color()),
        outside_color=properties.get('outside', create_default_color()),
        rounded=properties.get('rounded', False)
    )