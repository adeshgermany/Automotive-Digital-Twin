import tkinter as tk
import can

root = tk.Tk()
root.title("Automotive Digital Twin Dashboard")
root.geometry("850x600")
root.configure(bg="#101820")

title = tk.Label(
    root,
    text="AUTOMOTIVE DIGITAL TWIN",
    font=("Arial", 24, "bold"),
    fg="cyan",
    bg="#101820"
)
title.pack(pady=20)

labels = {}

parameters = [
    "Speed",
    "RPM",
    "Engine Temperature",
    "Battery Voltage",
    "Battery Current",
    "Battery SOC",
    "Battery Temperature"
]

for parameter in parameters:
    label = tk.Label(
        root,
        text=f"{parameter}: --",
        font=("Arial", 18),
        fg="white",
        bg="#101820"
    )
    label.pack(pady=8)
    labels[parameter] = label

bus = can.Bus(
    channel="vcan0",
    interface="socketcan"
)

def update_dashboard():

    for _ in range(50):
        msg = bus.recv(timeout=0.0)

        if msg is None:
            break

        data = msg.data

        if msg.arbitration_id == 0x100 and len(data) >= 5:

            speed = int.from_bytes(
                data[0:2], "big"
            )

            rpm = int.from_bytes(
                data[2:4], "big"
            )

            temperature = data[4]

            labels["Speed"].config(
                text=f"Speed: {speed} km/h"
            )

            labels["RPM"].config(
                text=f"RPM: {rpm}"
            )

            labels["Engine Temperature"].config(
                text=f"Engine Temperature: {temperature} °C"
            )

        elif msg.arbitration_id == 0x200 and len(data) >= 8:

            voltage = int.from_bytes(
                data[0:2], "big"
            ) / 10

            current = int.from_bytes(
                data[2:4], "big", signed=True
            ) / 10

            soc = int.from_bytes(
                data[4:6], "big"
            ) / 100

            temperature = int.from_bytes(
                data[6:8], "big", signed=True
            ) / 10

            labels["Battery Voltage"].config(
                text=f"Battery Voltage: {voltage:.1f} V"
            )

            labels["Battery Current"].config(
                text=f"Battery Current: {current:.1f} A"
            )

            labels["Battery SOC"].config(
                text=f"Battery SOC: {soc:.2f} %"
            )

            labels["Battery Temperature"].config(
                text=f"Battery Temperature: {temperature:.1f} °C"
            )

    root.after(100, update_dashboard)

def close_dashboard():
    bus.shutdown()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_dashboard)

update_dashboard()

root.mainloop()


