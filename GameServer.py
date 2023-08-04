import asyncio
import tkinter as tk
import concurrent.futures
import socket

async def handle_client(reader, writer, player_name, move_callback):
    while True:
        data = await reader.readline()
        if not data:
            break
        move_callback(f"{player_name} made move {data.decode().strip()}")
        await asyncio.sleep(1) # the opponent takes 55 seconds to make a move
        writer.write("your turn\n".encode())
        await writer.drain()

    writer.close()

async def play_game(player_name, reader, writer, move_callback):
    while True:
        writer.write("your turn\n".encode())
        await writer.drain()
        data = await reader.readline()
        if not data:
            break
        move_callback(f"{player_name} made move {data.decode().strip()}")
        await asyncio.sleep(5) # the champion takes 5 seconds to make a move

    writer.close()

async def play_all_games(players, port, move_callback):
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, "Spectator", move_callback), '', port)

    tasks = []
    for player_name, address in players:
        reader, writer = await asyncio.open_connection(*address)
        task = asyncio.create_task(play_game(player_name, reader, writer, move_callback))
        tasks.append(task)

    tasks.append(asyncio.create_task(server.serve_forever()))

    await asyncio.gather(*tasks)

def start_game():
    players = []
    for i in range(int(num_players.get())):
        player_name = player_names[i].get()
        address = (ip_addresses[i].get(), int(port.get()))
        players.append((player_name, address))
    executor.submit(asyncio.run, play_all_games(players, int(port.get()), update_text))

def update_text(text):
    text_box.config(state=tk.NORMAL)
    text_box.insert(tk.END, text + "\n")
    text_box.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Game")

    num_players_label = tk.Label(root, text="Number of players:")
    num_players_label.pack()

    num_players = tk.Entry(root)
    num_players.pack()

    port_label = tk.Label(root, text="Port Number:")
    port_label.pack()

    port = tk.Entry(root)
    port.pack()

    player_names = []
    ip_addresses = []

    for i in range(4):
        player_frame = tk.Frame(root)
        player_frame.pack()

        player_label = tk.Label(player_frame, text=f"Player {i+1} Name:")
        player_label.pack(side=tk.LEFT)

        player_name = tk.Entry(player_frame)
        player_name.pack(side=tk.LEFT)
        player_names.append(player_name)

        ip_label = tk.Label(player_frame, text=f"IP Address {i+1}:")
        ip_label.pack(side=tk.LEFT)

        ip_address = tk.Entry(player_frame)
        ip_address.pack(side=tk.LEFT)
        ip_addresses.append(ip_address)

    start_button = tk.Button(root, text="Start Game", command=start_game)
    start_button.pack()

    text_box = tk.Text(root, width=150, height=80, state=tk.DISABLED)
    text_box.pack()

    executor = concurrent.futures.ThreadPoolExecutor()
    root.mainloop()

    executor.shutdown()
