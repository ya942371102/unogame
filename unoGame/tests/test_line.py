import tkinter as tk

root = tk.Tk()
root.title("Line with Thin Ends and Thick Center")

canvas = tk.Canvas(root, width=200, height=100, bg="white")
canvas.pack()

# Define the coordinates of the line (x1, y1, x2, y2)
x1, y1 = 20, 50
x2, y2 = 180, 50

# Set colors for the ends and the center
color_start = "lightblue"
color_end = "lightblue"
color_center = "blue"

# Set thickness for the ends and the center
width_start = 3
width_end = 3
width_center = 10

# Draw the line with different colors and thicknesses
canvas.create_line(x1, y1, (x1 + x2) / 2, y2, fill=color_start, width=width_start, capstyle="round")
canvas.create_line((x1 + x2) / 2, y1, x2, y2, fill=color_end, width=width_end, capstyle="round")
canvas.create_line(x1, y1, x2, y2, fill=color_center, width=width_center, capstyle="round")

root.mainloop()
