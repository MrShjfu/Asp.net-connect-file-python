
# noinspection PyUnresolvedReferences
import Tkinter,tkFileDialog
from stitching import main
# noinspection PyUnresolvedReferences
from Tkinter import *
from tkFileDialog import *

class Application(Frame):
    def main(self):
        self.filename = askopenfilenames(filetypes=(
                                           ("images files", "*.jpg;*.png"),
                                           ("All files", "*.*") ))
        a = list(self.filename)[:]
        a.sort()
        if __name__ == '__main__':
            main(a)
    def createWidgets(self):
        self.button = Button(root,text="Open",command=self.main)
        self.button.pack()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.filename = None
        self.createWidgets()

root = Tk()

root.title("Image Manipulation Program")
root.geometry("200x50")
app = Application(master=root)
print app.filename
app.mainloop()


