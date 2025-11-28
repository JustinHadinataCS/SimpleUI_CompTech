"""
SimpleUI Compiler - Main Entry Point
Orchestrates lexer, parser, and code generator
"""

import sys
import os
import argparse
from pathlib import Path

# Import compiler components
from lexer import Lexer, LexerError, tokenize_string
from parser import Parser, parse_string
from code_generator import CodeGenerator, generate_to_file
import ast_nodes


class CompilerError(Exception):
    """Base exception for compiler errors"""
    pass


class SimpleUICompiler:
    """Main compiler class that orchestrates the compilation pipeline"""
    
    def __init__(self, grammar_file: str = 'grammar.lark', verbose: bool = False):
        """
        Initialize the compiler
        
        Args:
            grammar_file: Path to grammar specification
            verbose: Enable verbose output for debugging
        """
        self.grammar_file = grammar_file
        self.verbose = verbose
        self.lexer = None
        self.parser = None
        self.generator = None
        
        # Initialize components
        try:
            self.parser = Parser(grammar_file)
            self.generator = CodeGenerator()
            if self.verbose:
                print(f"✓ Compiler initialized with grammar: {grammar_file}")
        except Exception as e:
            raise CompilerError(f"Failed to initialize compiler: {e}")
    
    def compile_string(self, source_code: str) -> str:
        """
        Compile SimpleUI source code string to Python/Turtle code
        
        Args:
            source_code: SimpleUI source code as string
            
        Returns:
            Generated Python code as string
            
        Raises:
            CompilerError: If compilation fails at any stage
        """
        try:
            # Stage 1: Lexical Analysis (Optional - Lark handles this)
            if self.verbose:
                print("\n[Stage 1] Lexical Analysis...")
                self.lexer = Lexer(source_code)
                tokens = self.lexer.tokenize()
                print(f"  Tokens generated: {len(tokens)}")
                if self.verbose:
                    for token in tokens[:10]:  # Show first 10 tokens
                        print(f"    {token}")
                    if len(tokens) > 10:
                        print(f"    ... and {len(tokens) - 10} more tokens")
            
            # Stage 2: Parsing
            if self.verbose:
                print("\n[Stage 2] Parsing...")
            
            ast = self.parser.parse(source_code)
            
            if self.verbose:
                print(f"  AST generated: {len(ast.shapes)} shapes")
                for i, shape in enumerate(ast.shapes, 1):
                    print(f"    Shape {i}: {shape.shape_type} at {shape.position}")
            
            # Stage 3: Code Generation
            if self.verbose:
                print("\n[Stage 3] Code Generation...")
            
            generated_code = self.generator.generate(ast)
            
            if self.verbose:
                print(f"  Generated code: {len(generated_code)} characters")
            
            return generated_code
            
        except LexerError as e:
            raise CompilerError(f"Lexical error: {e}")
        except ValueError as e:
            raise CompilerError(f"Semantic error: {e}")
        except Exception as e:
            raise CompilerError(f"Compilation error: {e}")
    
    def compile_file(self, input_file: str, output_file: str = None, run: bool = False) -> str:
        """
        Compile a .sui file to Python/Turtle code
        
        Args:
            input_file: Path to .sui source file
            output_file: Path to output .py file (optional, defaults to input_file.py)
            run: If True, execute the generated code after compilation
            
        Returns:
            Path to generated output file
            
        Raises:
            CompilerError: If compilation fails
        """
        # Validate input file
        if not os.path.exists(input_file):
            raise CompilerError(f"Input file not found: {input_file}")
        
        # Read source code
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            raise CompilerError(f"Failed to read input file: {e}")
        
        # Determine output file name
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix('.py'))
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"SimpleUI Compiler")
            print(f"{'='*60}")
            print(f"Input:  {input_file}")
            print(f"Output: {output_file}")
            print(f"{'='*60}")
        
        # Compile
        try:
            generated_code = self.compile_string(source_code)
            
            # Write to output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            
            if self.verbose:
                print(f"\n✓ Compilation successful!")
                print(f"✓ Output written to: {output_file}")
            else:
                print(f"Compiled: {input_file} -> {output_file}")
            
            # Run if requested
            if run:
                if self.verbose:
                    print(f"\n[Executing] Running generated code...")
                import subprocess
                subprocess.run([sys.executable, output_file])
            
            return output_file
            
        except CompilerError as e:
            raise e
        except Exception as e:
            raise CompilerError(f"Failed to write output file: {e}")
    
    def compile_and_run(self, input_file: str):
        """Compile and immediately execute the generated code"""
        return self.compile_file(input_file, run=True)


def main():
    """Command-line interface for the compiler"""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='SimpleUI Compiler - Compile declarative UI descriptions to Python/Turtle graphics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compile a .sui file
  python compiler.py input.sui
  
  # Compile and specify output file
  python compiler.py input.sui -o output.py
  
  # Compile and run immediately
  python compiler.py input.sui --run
  
  # Verbose mode (show compilation stages)
  python compiler.py input.sui -v
  
  # Custom grammar file
  python compiler.py input.sui -g custom_grammar.lark
        """
    )
    
    parser.add_argument('input', help='Input .sui file')
    parser.add_argument('-o', '--output', help='Output .py file (default: input.py)')
    parser.add_argument('-r', '--run', action='store_true', help='Run the generated code after compilation')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-g', '--grammar', default='grammar.lark', help='Grammar file (default: grammar.lark)')
    
    args = parser.parse_args()
    
    # Create compiler instance
    try:
        compiler = SimpleUICompiler(grammar_file=args.grammar, verbose=args.verbose)
        
        # Compile
        output_file = compiler.compile_file(
            input_file=args.input,
            output_file=args.output,
            run=args.run
        )
        
        if not args.run and not args.verbose:
            print(f"\nTo run the generated code:")
            print(f"  python {output_file}")
        
        sys.exit(0)
        
    except CompilerError as e:
        print(f"\n❌ Compilation failed:", file=sys.stderr)
        print(f"   {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCompilation interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error:", file=sys.stderr)
        print(f"   {e}", file=sys.stderr)
        sys.exit(1)


# Testing functions
def run_tests():
    """Run built-in compiler tests"""
    print("="*60)
    print("SimpleUI Compiler - Running Tests")
    print("="*60)
    
    # Test 1: Basic compilation
    print("\n[Test 1] Basic Rectangle")
    test_code_1 = """
    100px left, 50px top, w:200px, h:100px, fill:#FF0000, outside:#000000, rounded, rectangle;
    """
    
    try:
        compiler = SimpleUICompiler(verbose=True)
        code = compiler.compile_string(test_code_1)
        print("✓ Test 1 passed")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
    
    # Test 2: Multiple shapes
    print("\n[Test 2] Multiple Shapes with Defaults")
    test_code_2 = """
    w:100px, h:100px, circle;
    50px left, 50px top, w:150px, h:75px, fill:#00FF00, rectangle;
    """
    
    try:
        compiler = SimpleUICompiler(verbose=False)
        code = compiler.compile_string(test_code_2)
        print("✓ Test 2 passed")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
    
    # Test 3: Error handling
    print("\n[Test 3] Error Handling (Missing Width)")
    test_code_3 = "h:100px, rectangle;"
    
    try:
        compiler = SimpleUICompiler(verbose=False)
        code = compiler.compile_string(test_code_3)
        print("✗ Test 3 failed: Should have raised error")
    except CompilerError as e:
        print(f"✓ Test 3 passed: Error correctly caught")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)


if __name__ == "__main__":
    # If no arguments provided, run tests
    if len(sys.argv) == 1:
        print("No input file provided. Running built-in tests...\n")
        run_tests()
        print("\nUsage: python compiler.py <input.sui> [options]")
        print("Run 'python compiler.py --help' for more information")
    else:
        main()