from tkinter import *
from tkinter import ttk
import convoDemo.py
from tkinter import messagebox
from tkinter import scrolledtext

with open('sent_tokenizer.pickle', 'rb') as f:
    sent_tokenizer=pickle.load(f)

sub = ""

root = Tk()
root.geometry("1280x720+0+0")
root.title("Charles the Chatbot")

topFrame = Frame(root,height =600,width=1280,bg ="blue",cursor = "dot",borderwidth=5,relief="groove").grid(row=0,column=0)
botFrame = Frame(root,height=80,width=1280,bg="red",bd=11,relief=SUNKEN).grid(row=1,column=0)

rep = StringVar()
textbox = ttk.Entry(width = 205, textvariable=rep).grid(row=1, column=0, sticky=W, padx=15)




root.mainloop()