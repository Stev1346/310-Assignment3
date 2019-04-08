import tkinter
from _multiprocessing import send
from tkinter import *
from tkinter import ttk

from tkinter import messagebox
from tkinter import scrolledtext

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

root = Tk()

root.resizable(0,0)
root.title("Charles the Chatbot")

topFrame = Frame(root)
topFrame.pack()
botFrame = Frame(root, width=400, height=75)
botFrame.pack(side=BOTTOM)

msgFrame = tkinter.Frame(topFrame)
myMsg = tkinter.StringVar()
myMsg.set("")
scrollbar = tkinter.Scrollbar(msgFrame)

msgList = tkinter.Listbox(msgFrame, height =15, width = 50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msgList.pack(side=tkinter.LEFT,fill=tkinter.BOTH)
msgList.pack()

msgFrame.pack()

msgInput = tkinter.Entry(root, textvariable=myMsg)
msgInput.bind("<Return>",send)
msgInput.pack()
sendButton = tkinter.Button(root, text="Send", command = send)
sendButton.pack()

def send(event=None):
    myMsg = "You: " + msgInput.get()

    if myMsg == "{quit}" or 'bye' in myMsg:
        root.quit()
    else:
        call()
        msgList.insert(END, myMsg)
        msgList.yview(END)
        msgInput.delete(0, 'end')

def call(event=None):
    print(msgInput.get())

root.mainloop()
