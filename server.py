import asyncio
import tkinter as tk
from tkinter import scrolledtext
import websockets
import threading

connected = set()

async def chat(websocket, path):
    connected.add(websocket)
    try:
        async for message in websocket:
            display_message(f"Client says: {message}")
            for conn in connected:
                if conn != websocket:
                    await conn.send(f"Client says: {message}")
    finally:
        connected.remove(websocket)

def display_message(message):
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, message + '\n')
    chat_box.configure(state='disabled')
    chat_box.yview(tk.END)

def send_message():
    message = message_entry.get()
    message_entry.delete(0, tk.END)
    display_message(f"Server says: {message}")
    for conn in connected:
        asyncio.run_coroutine_threadsafe(conn.send(f"Server says: {message}"), loop)

# Set up the Tkinter GUI
root = tk.Tk()
root.title("WebSocket Server")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

chat_box = scrolledtext.ScrolledText(frame, state='disabled', width=50, height=10)
chat_box.pack()

message_entry = tk.Entry(frame, width=43)
message_entry.pack(side=tk.LEFT)

send_button = tk.Button(frame, text="Send", command=send_message)
send_button.pack(side=tk.LEFT, padx=5)

# Run the WebSocket server in a separate thread
def run_server():
    asyncio.set_event_loop(loop)  # Set the event loop in this thread
    loop.run_until_complete(websockets.serve(chat, "localhost", 8765))
    loop.run_forever()

loop = asyncio.new_event_loop()
threading.Thread(target=run_server, daemon=True).start()

# Run the Tkinter event loop in the main thread
root.mainloop()
