import tkinter as tk
from PIL import ImageTk, Image


def show_toast(message):
    toast = tk.Toplevel()
    toast.wm_overrideredirect(True)  # Remove window decorations
    toast.wm_geometry("+{}+{}".format(root.winfo_screenwidth() // 2, root.winfo_screenheight() // 2))
    image = Image.open('../images/LOGO.png')
    image = image.resize((120, 90))
    image=ImageTk.PhotoImage(image)

    label = tk.Label(toast, image=image)
    label.image=image
    label.pack(padx=10, pady=5)

    # After 2000 milliseconds (2 seconds), close the toast
    toast.after(1000, toast.destroy)


# Create the main application window
root = tk.Tk()
root.title("Tkinter Toast Example")

# Button to trigger the toast
button = tk.Button(root, text="Show Toast", command=lambda: show_toast("This is a toast message!"))
button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
