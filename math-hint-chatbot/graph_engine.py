import os
import uuid
import numpy as np
import matplotlib.pyplot as plt

from sympy import (
    symbols,
    sympify,
    diff,
    integrate,
    solveset,
    S,
    lambdify,
    Eq,
    solve,
)

x = symbols("x")


class GraphEngine:

    def __init__(self):

        self.graph_folder = "graphs"

        os.makedirs(self.graph_folder, exist_ok=True)

    # -----------------------------------
    # Parse Equation
    # -----------------------------------

    def parse_equation(self, equation: str):

        equation = equation.replace("^", "**")

        return sympify(equation)

    # -----------------------------------
    # Function Type
    # -----------------------------------

    def function_type(self, expr):

        s = str(expr).lower()

        if "sin" in s:
            return "Trigonometric"

        if "cos" in s:
            return "Trigonometric"

        if "tan" in s:
            return "Trigonometric"

        if "log" in s:
            return "Logarithmic"

        if "exp" in s:
            return "Exponential"

        if expr.is_polynomial():
            return "Polynomial"

        return "General Function"

    # -----------------------------------
    # Domain
    # -----------------------------------

    def get_domain(self, expr):

        try:

            domain = solveset(Eq(0, 0), x, domain=S.Reals)

            return str(domain)

        except:

            return "All Real Numbers"

    # -----------------------------------
    # Roots
    # -----------------------------------

    def get_roots(self, expr):

        try:

            roots = solve(expr, x)

            return [str(r) for r in roots]

        except:

            return []

    # -----------------------------------
    # Y Intercept
    # -----------------------------------

    def get_y_intercept(self, expr):

        try:

            return str(expr.subs(x, 0))

        except:

            return "Not Found"
            # -----------------------------------
    # Derivative
    # -----------------------------------

    def get_derivative(self, expr):

        try:

            derivative = diff(expr, x)

            return derivative

        except:

            return None

    # -----------------------------------
    # Integral
    # -----------------------------------

    def get_integral(self, expr):

        try:

            integral = integrate(expr, x)

            return integral

        except:

            return None

    # -----------------------------------
    # Critical Points
    # -----------------------------------

    def get_critical_points(self, expr):

        try:

            derivative = diff(expr, x)

            points = solve(derivative, x)

            return [str(point) for point in points]

        except:

            return []

    # -----------------------------------
    # Increasing / Decreasing
    # -----------------------------------

    def get_monotonicity(self, expr):

        try:

            derivative = diff(expr, x)

            critical = solve(derivative, x)

            return {
                "derivative": str(derivative),
                "critical_points": [str(i) for i in critical]
            }

        except:

            return {
                "derivative": "Not Available",
                "critical_points": []
            }

    # -----------------------------------
    # Generate AI Hints
    # -----------------------------------

    def generate_hints(self, expr):

        hints = []

        function_name = self.function_type(expr)

        hints.append(
            f"This is a {function_name} function."
        )

        if expr.is_polynomial():

            degree = expr.as_poly().degree()

            hints.append(
                f"It is a polynomial of degree {degree}."
            )

        derivative = self.get_derivative(expr)

        if derivative is not None:

            hints.append(
                "Differentiate the function to study its behaviour."
            )

        roots = self.get_roots(expr)

        if len(roots):

            hints.append(
                "Find where the function becomes zero."
            )

        hints.append(
            "Observe the graph before solving analytically."
        )

        return hints
        # -----------------------------------
    # Generate Graph
    # -----------------------------------

    def generate_graph(self, expr):

        func = lambdify(x, expr, modules=["numpy"])

        x_values = np.linspace(-10, 10, 600)

        try:
            y_values = func(x_values)
        except Exception:
            y_values = np.zeros_like(x_values)

        plt.figure(figsize=(8, 6))

        plt.plot(
            x_values,
            y_values,
            linewidth=2.5,
            label=f"y = {expr}"
        )

        # X and Y axes
        plt.axhline(0, linewidth=1)
        plt.axvline(0, linewidth=1)

        # Grid
        plt.grid(True, linestyle="--", alpha=0.4)

        # Labels
        plt.xlabel("x")
        plt.ylabel("y")

        plt.title("AI Graph Visualizer")

        plt.legend()

        # Save graph
        filename = f"{uuid.uuid4().hex}.png"

        filepath = os.path.join(
            self.graph_folder,
            filename
        )

        plt.savefig(
            filepath,
            dpi=200,
            bbox_inches="tight"
        )

        plt.close()

        return filepath.replace("\\", "/")

    # -----------------------------------
    # Graph Information
    # -----------------------------------

    def get_graph_info(self, expr):

        return {

            "roots": self.get_roots(expr),

            "y_intercept": self.get_y_intercept(expr),

            "derivative": str(
                self.get_derivative(expr)
            ),

            "integral": str(
                self.get_integral(expr)
            ) + " + C",

            "critical_points":
                self.get_critical_points(expr),

            "domain":
                self.get_domain(expr),

            "function_type":
                self.function_type(expr),

            "hints":
                self.generate_hints(expr)

        }
            # -----------------------------------
    # Analyze Equation
    # -----------------------------------

    def analyze(self, equation):

        try:

            # Parse equation
            expr = self.parse_equation(equation)

            # Generate graph image
            graph_path = self.generate_graph(expr)

            # Collect all mathematical information
            info = self.get_graph_info(expr)

            # Return complete response
            return {

                "status": "success",

                "equation": str(expr),

                "graph": graph_path,

                "function_type": info["function_type"],

                "domain": info["domain"],

                "roots": info["roots"],

                "y_intercept": info["y_intercept"],

                "derivative": info["derivative"],

                "integral": info["integral"],

                "critical_points": info["critical_points"],

                "hints": info["hints"]

            }

        except Exception as e:

            return {

                "status": "error",

                "message": str(e)

            }
