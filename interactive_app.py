"""
SimpleUI Interactive Application
A live coding environment with text input and visual output
"""

import turtle
import tkinter as tk
from tkinter import scrolledtext, messagebox
from parser import Parser
from code_generator import CodeGenerator
import ast_nodes


class SimpleUIApp:
    """Interactive SimpleUI compiler and renderer"""
    
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("SimpleUI Interactive Compiler")
        self.root.geometry("1200x700")
        
        # Initialize parser and generator
        try:
            self.parser = Parser()
            self.generator = CodeGenerator()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize compiler: {e}")
            self.root.destroy()
            return
        
        # Create UI components
        self.setup_ui()
        
        # Turtle setup
        self.canvas = None
        self.screen = None
        self.turtle = None
        self.setup_turtle()
        
        # Default example code
        self.load_example()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title = tk.Label(self.root, text="SimpleUI Interactive Compiler", 
                        font=("Arial", 16, "bold"), bg="#2c3e50", fg="white", pady=10)
        title.pack(fill=tk.X)
        
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Code editor
        left_frame = tk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Editor label
        editor_label = tk.Label(left_frame, text="SimpleUI Code Editor", 
                               font=("Arial", 12, "bold"), anchor="w")
        editor_label.pack(fill=tk.X, pady=(0, 5))
        
        # Text editor
        self.text_editor = scrolledtext.ScrolledText(
            left_frame, 
            wrap=tk.WORD, 
            font=("Courier", 11),
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="white",
            selectbackground="#4a4a4a"
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Compile button
        compile_btn = tk.Button(
            button_frame, 
            text="▶ Compile & Render", 
            command=self.compile_and_render,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        )
        compile_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="Clear Canvas",
            command=self.clear_canvas,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Example button
        example_btn = tk.Button(
            button_frame,
            text="Load Example",
            command=self.load_example,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8
        )
        example_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            left_frame,
            text="Ready to compile",
            font=("Arial", 10),
            fg="#7f8c8d",
            anchor="w"
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Right side - Canvas display
        right_frame = tk.Frame(main_container, bg="white", relief=tk.SUNKEN, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Canvas label
        canvas_label = tk.Label(right_frame, text="Visual Output", 
                               font=("Arial", 12, "bold"), bg="white", anchor="w")
        canvas_label.pack(fill=tk.X, pady=(5, 5), padx=5)
        
        # Turtle canvas container
        self.turtle_container = tk.Frame(right_frame, bg="white")
        self.turtle_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    def setup_turtle(self):
        """Setup turtle graphics canvas"""
        try:
            self.canvas = tk.Canvas(self.turtle_container, width=550, height=550, bg="white")
            self.canvas.pack()
            
            self.screen = turtle.TurtleScreen(self.canvas)
            self.screen.bgcolor("white")
            # [FIX] Turn off animation tracer for instant drawing and stability
            self.screen.tracer(0)
            
            self.turtle = turtle.RawTurtle(self.screen)
            self.turtle.speed(0)
            self.turtle.hideturtle()
            
        except Exception as e:
            messagebox.showerror("Turtle Error", f"Failed to setup turtle: {e}")
    
    def clear_canvas(self):
        """Clear the turtle canvas"""
        if self.turtle and self.screen:
            self.turtle.clear()
            self.turtle.penup()
            # Reset to home (center)
            self.turtle.goto(0, 0)
            self.turtle.setheading(0) # Reset angle
            self.screen.update()
            self.update_status("Canvas cleared", "info")
    
    def load_example(self):
        """Load example code into editor"""
        example_code = """// W - using lines and rectangles
150px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;
150px left, 135px top, w:30px, h:5px, fill:#000000, rectangle;
180px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;
184px left, 135px top, w:30px, h:5px, fill:#000000, rectangle;
210px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;

// E
230px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;
230px left, 80px top, w:30px, h:5px, fill:#000000, rectangle;
230px left, 107px top, w:28px, h:5px, fill:#000000, rectangle;
230px left, 135px top, w:30px, h:5px, fill:#000000, rectangle;

// L
275px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;
275px left, 135px top, w:28px, h:5px, fill:#000000, rectangle;

// C
320px left, 80px top, w:30px, h:5px, fill:#000000, rectangle;
320px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;
320px left, 135px top, w:30px, h:5px, fill:#000000, rectangle;

// O - circle
370px left, 80px top, w:40px, h:40px, fill:#FFFFFF, outside:#000000, circle;

// M
430px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;
435px left, 80px top, w:18px, h:5px, fill:#000000, rectangle;
450px left, 85px top, w:10px, h:30px, fill:#000000, rectangle;
450px left, 80px top, w:25px, h:5px, fill:#000000, rectangle;
473px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;

// E
495px left, 80px top, w:5px, h:60px, fill:#000000, rectangle;
495px left, 80px top, w:30px, h:5px, fill:#000000, rectangle;
495px left, 107px top, w:28px, h:5px, fill:#000000, rectangle;
495px left, 135px top, w:30px, h:5px, fill:#000000, rectangle;

// "To" - Second line
250px left, 170px top, w:5px, h:55px, fill:#000000, rectangle;
243px left, 170px top, w:19px, h:5px, fill:#000000, rectangle;

285px left, 175px top, w:40px, h:40px, fill:#FFFFFF, outside:#000000, circle;

// "SimpleUI" - Third line
// S
150px left, 260px top, w:30px, h:5px, fill:#000000, rectangle;
150px left, 260px top, w:5px, h:28px, fill:#000000, rectangle;
150px left, 285px top, w:30px, h:5px, fill:#000000, rectangle;
175px left, 285px top, w:5px, h:28px, fill:#000000, rectangle;
150px left, 310px top, w:30px, h:5px, fill:#000000, rectangle;

// i
195px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;

// m
215px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;
220px left, 260px top, w:15px, h:5px, fill:#000000, rectangle;
235px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;
240px left, 260px top, w:15px, h:5px, fill:#000000, rectangle;
255px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;

// p
275px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;
275px left, 260px top, w:25px, h:5px, fill:#000000, rectangle;
300px left, 260px top, w:5px, h:28px, fill:#000000, rectangle;
275px left, 285px top, w:30px, h:5px, fill:#000000, rectangle;

// l
320px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;

// e
340px left, 260px top, w:30px, h:5px, fill:#000000, rectangle;
340px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;
340px left, 285px top, w:28px, h:5px, fill:#000000, rectangle;
340px left, 310px top, w:30px, h:5px, fill:#000000, rectangle;

// U
385px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;
385px left, 310px top, w:30px, h:5px, fill:#000000, rectangle;
410px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;

// I
430px left, 260px top, w:5px, h:53px, fill:#000000, rectangle;
"""
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, example_code)
        self.update_status("Example loaded", "info")
    
    def update_status(self, message, status_type="info"):
        """Update status label with color coding"""
        colors = {
            "info": "#3498db",
            "success": "#27ae60",
            "error": "#e74c3c"
        }
        self.status_label.config(text=message, fg=colors.get(status_type, "#7f8c8d"))
        self.root.update()
    
    def draw_shape(self, shape: ast_nodes.Shape):
        """Draw a single shape using turtle with DEBUG prints"""
        t = self.turtle
        
        # 1. DEBUG: Check what the shape_type actually is
        print(f"DEBUG: Processing Shape...")
        print(f"   -> Type in AST: {type(shape.shape_type)}")
        print(f"   -> Value: '{shape.shape_type}'")
        
        # FORCE FIX: Convert to string to ensure 'if' statements work
        # This handles cases where it might still be a Lark Token object
        s_type = str(shape.shape_type).lower()
        
        # Calculate Coordinates
        t.penup()
        start_x = shape.position.x - 275  
        start_y = 275 - shape.position.y 
        
        print(f"   -> Calculated Coords: x={start_x}, y={start_y}")

        # Set colors
        if shape.fill_color:
            t.fillcolor(shape.fill_color.hex_value.lower())
        if shape.outside_color:
            t.pencolor(shape.outside_color.hex_value.lower())
        
        # Use the forced string 's_type' for comparison
        if s_type == 'rectangle':
            print("   -> MATCH: Drawing Rectangle") # Debug print
            t.goto(start_x, start_y)
            t.setheading(0)
            t.pendown()
            t.begin_fill()
            
            if shape.rounded:
                radius = min(10, shape.size.width / 10, shape.size.height / 10)
                # Draw Clockwise (Downwards)
                t.forward(shape.size.width - 2*radius)
                t.circle(-radius, 90) 
                t.forward(shape.size.height - 2*radius)
                t.circle(-radius, 90)
                t.forward(shape.size.width - 2*radius)
                t.circle(-radius, 90)
                t.forward(shape.size.height - 2*radius)
                t.circle(-radius, 90)
            else:
                for _ in range(2):
                    t.forward(shape.size.width)
                    t.right(90)
                    t.forward(shape.size.height)
                    t.right(90)
            
            t.end_fill()
            
        elif s_type == 'circle':
            print("   -> MATCH: Drawing Circle") # Debug print
            radius = min(shape.size.width, shape.size.height) / 2
            center_x = start_x + (shape.size.width / 2)
            center_y = start_y - (shape.size.height / 2)
            
            t.goto(center_x, center_y - radius)
            t.setheading(0)
            t.pendown()
            t.begin_fill()
            t.circle(radius)
            t.end_fill()
            
        elif s_type == 'line':
            print("   -> MATCH: Drawing Line") # Debug print
            t.goto(start_x, start_y)
            t.pendown()
            t.goto(start_x + shape.size.width, start_y - shape.size.height)
        
        else:
            print(f"   -> FAIL: Shape '{s_type}' did not match 'rectangle', 'circle', or 'line'")
            
    def compile_and_render(self):
        """Compile code and render on canvas"""
        source_code = self.text_editor.get(1.0, tk.END)
        
        if not source_code.strip():
            self.update_status("No code to compile", "error")
            return
        
        try:
            self.update_status("Compiling...", "info")
            self.root.update()
            
            ast = self.parser.parse(source_code)
            
            self.clear_canvas()
            
            for shape in ast.shapes:
                self.draw_shape(shape)
            
            # [FIX] Explicit update needed because tracer is 0
            self.screen.update()
            self.update_status(f"✓ Compiled successfully! {len(ast.shapes)} shape(s) rendered", "success")
            
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"✗ Error: {error_msg}", "error")
            messagebox.showerror("Compilation Error", f"Failed to compile:\n\n{error_msg}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = SimpleUIApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()