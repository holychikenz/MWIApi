import matplotlib.pyplot as plt
import sqlite3
import numpy as np

def plot_holy_milk():
    conn = sqlite3.connect('market.db')
    cursor = conn.cursor()

    cursor.execute("SELECT time, \"Holy Milk\" FROM ask ORDER BY time")
    data = cursor.fetchall()
    conn.close()

    if not data:
        print("No data found.")
        return

    times, holy_milk = zip(*data)
    times = np.array(times)
    holy_milk = np.array(holy_milk)

    median = np.median(holy_milk)
    threshold = median * 5

    times = times[holy_milk < threshold]
    holy_milk = holy_milk[holy_milk < threshold]

    plt.figure(figsize=(10, 5))
    plt.plot(times, holy_milk, marker='o', linestyle='-', color='blue')
    plt.title('Holy Milk Prices Over Time')
    plt.xlabel('Time')
    plt.ylabel('Holy Milk Price')
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_holy_milk()

