import tkinter as tk
from threading import Thread
import time
import lumira_core

from lumira_core import listen_to_wake, listen_command, execute_command, speak, wish_user, TMDB_API

running = False

def update_output(text):
    output_box.config(state=tk.NORMAL)

    for char in text:
        output_box.insert(tk.END, char)
        output_box.update()
        time.sleep(0.01)   

    output_box.insert(tk.END, "\n")
    output_box.config(state=tk.DISABLED)
    output_box.see(tk.END)

def safe_update_output(text):
    root.after(0, lambda: update_output(text))

lumira_core.ui_callback = safe_update_output


def set_status(text):
    root.after(0, lambda: status_label.config(text=f"Status: {text}"))

def set_mic(color):
    root.after(0, lambda: mic_label.config(fg=color))



def start_assistant():
    global running

    if not running:
        running = True
        lumira_core.stop_speech_flag = False

        start_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)

        Thread(target=run_assistant, daemon=True).start()

def stop_assistant():
    global running
    running = False

    lumira_core.stop_speaking()

    set_status("Stopped")
    update_output("Assistant stopped.")

    root.after(100, lambda: speak("On idle mode, call me whenever you need me"))

    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)



def send_text_command():
    command = input_box.get()
    input_box.delete(0, tk.END)

    if command:
        safe_update_output("You: " + command)
        execute_command(command, TMDB_API)



def run_assistant():
    speak("Hello. Lumira is now online")
    wish_user()

    while running:
        if lumira_core.should_stop():
            break

        set_status("Idle")
        set_mic("gray")

        listen_to_wake()

        if not running:
            break

        last_activity = time.time()

        while running:
            if lumira_core.should_stop():
                break

            set_status("Listening")
            set_mic("red")

            command = listen_command()

            set_mic("gray")

            if command:
                safe_update_output("You: " + command)

                set_status("Processing")

                last_activity = time.time()

                if "sleep" in command or "goodbye" in command:
                    speak("Going to sleep.")
                    break

                execute_command(command, TMDB_API)

            if time.time() - last_activity > 30:
                speak("Going idle now")
                break



root = tk.Tk()
root.title("Lumira Assistant")
root.geometry("500x650")
root.configure(bg="#0f172a")

title = tk.Label(root, text="LUMIRA", font=("Arial", 24, "bold"), fg="cyan", bg="#0f172a")
title.pack(pady=10)


status_label = tk.Label(root, text="Status: Idle", fg="yellow", bg="#0f172a", font=("Arial", 12))
status_label.pack()


mic_label = tk.Label(root, text="🎤", font=("Arial", 30), fg="gray", bg="#0f172a")
mic_label.pack(pady=5)


start_btn = tk.Button(root, text="Start", command=start_assistant, bg="green", fg="white", width=15)
start_btn.pack(pady=10)

stop_btn = tk.Button(root, text="Stop", command=stop_assistant, bg="red", fg="white", width=15, state=tk.DISABLED)
stop_btn.pack(pady=10)



chat_frame = tk.Frame(root, bg="#0f172a")
chat_frame.pack(pady=10)


input_box = tk.Entry(chat_frame, width=40, font=("Arial", 12))
input_box.grid(row=0, column=0, padx=5, pady=5)

send_btn = tk.Button(chat_frame, text="Send", command=send_text_command, bg="blue", fg="white")
send_btn.grid(row=0, column=1, padx=5)


input_box.bind("<Return>", lambda event: send_text_command())


output_frame = tk.Frame(chat_frame)
output_frame.grid(row=1, column=0, columnspan=2)

scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_box = tk.Text(
    output_frame,
    height=18,
    width=55,
    bg="black",
    fg="lime",
    yscrollcommand=scrollbar.set
)
output_box.pack(side=tk.LEFT)

scrollbar.config(command=output_box.yview)
output_box.config(state=tk.DISABLED)



root.mainloop()