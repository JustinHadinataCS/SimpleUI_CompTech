"""
Semantic analyzer for SimpleUI AST

PURPOSE:
This module performs semantic validation and light normalization on the
AST produced by the parser. It checks invariants that go beyond syntax
(e.g. positive sizes, color node types, coordinate ranges) and can
annotate or normalize the AST for downstream code generation.

The analyzer raises `SemanticError` when an invariant is violated.
"""
from typing import Any
import ast_nodes


class SemanticError(Exception):
    """Raised when a semantic invariant is violated."""
    pass


class SemanticAnalyzer:
    """Validate and normalize a `ast_nodes.ShapeList`.

    Checks performed:
    - Each shape must have positive `width` and `height`.
    - `fill_color` and `outside_color` must be `ast_nodes.Color`.
    - Position coordinates must be non-negative.
    - For `circle` shapes, normalize size to a square using the smaller
      of width/height (so drawing logic can rely on a single radius).

    The analyzer mutates the AST in-place (light normalization) and
    returns the same AST for convenience.
    """

    def analyze(self, ast: ast_nodes.ShapeList) -> ast_nodes.ShapeList:
        if not isinstance(ast, ast_nodes.ShapeList):
            raise SemanticError("Expected ShapeList AST")

        for idx, shape in enumerate(ast.shapes, start=1):
            # Basic shape sanity
            if not isinstance(shape.size, ast_nodes.Size):
                raise SemanticError(f"Shape {idx}: missing size information")

            w = shape.size.width
            h = shape.size.height
            if w is None or h is None:
                raise SemanticError(f"Shape {idx}: width and height are required")
            if w <= 0 or h <= 0:
                raise SemanticError(
                    f"Shape {idx} ('{shape.shape_type}'): width and height must be positive (w={w}, h={h})"
                )

            # Normalize circle dimensions to a square using the smaller side
            if str(shape.shape_type).lower() == 'circle':
                if w != h:
                    m = min(w, h)
                    shape.size.width = m
                    shape.size.height = m

            # Colors should be Color instances (ast_nodes.Color normalizes values)
            if shape.fill_color is None or not isinstance(shape.fill_color, ast_nodes.Color):
                raise SemanticError(f"Shape {idx}: invalid or missing fill color")
            if shape.outside_color is None or not isinstance(shape.outside_color, ast_nodes.Color):
                raise SemanticError(f"Shape {idx}: invalid or missing outside color")

            # Positions should be present and non-negative (language expects pixels)
            if not isinstance(shape.position, ast_nodes.Position):
                raise SemanticError(f"Shape {idx}: invalid position information")
            if shape.position.x < 0 or shape.position.y < 0:
                raise SemanticError(
                    f"Shape {idx}: position coordinates must be non-negative (x={shape.position.x}, y={shape.position.y})"
                )

        return ast


__all__ = ["SemanticAnalyzer", "SemanticError"]
