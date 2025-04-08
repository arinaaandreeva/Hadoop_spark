import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

def load_metrics():
    files = [
        "metrics_1 DataNode.json",
        "metrics_1 DataNode_opt.json",
        "metrics_3 DataNodes.json",
        "metrics_3 DataNodes_opt.json"
    ]
    
    data = []
    for f in files:
        path = os.path.join("results", f)
        if os.path.exists(path):
            with open(path, "r") as fp:
                metrics = json.load(fp)
                is_optimized = "opt" in f
                nodes = "1 Node" if "1 DataNode" in metrics.get("cluster", "") else "3 Nodes"
                
                data.append({
                    "Configuration": f"{nodes} {'(Opt)' if is_optimized else ''}",
                    "Nodes": nodes,
                    "Optimized": is_optimized,
                    "Runtime (s)": metrics["runtime_sec"],
                    "Memory (MiB)": float(metrics["mem_used"].replace("MiB", "").strip())
                })
    
    return pd.DataFrame(data)

def calculate_speedups(df):
    speedups = []
    for nodes in ["1 Node", "3 Nodes"]:
        base = df[(df["Nodes"] == nodes) & (~df["Optimized"])]["Runtime (s)"].values[0]
        opt = df[(df["Nodes"] == nodes) & (df["Optimized"])]["Runtime (s)"].values[0]
        speedups.append({
            "Nodes": nodes,
            "Speedup": base / opt
        })
    return pd.DataFrame(speedups)


def plot_matplotlib_bar(x, y, xlabel, ylabel, title, colors=None):
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(x, y, color=colors)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    
    # Добавляем значения на столбцы
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    st.pyplot(fig)


def main():
    st.title("Сравнение работы Spark Application")
    
    df = load_metrics()
    
    # Таблица
    st.subheader("Results Summary")
    st.table(df[["Configuration", "Runtime (s)", "Memory (MiB)"]])
    
    colors = ['#1f77b4', '#ff7f0e', '#1f77b4', '#ff7f0e']  # Синий и оранжевый
    
    # время
    st.subheader("Сравнение времени")
    plot_matplotlib_bar(
        x=df["Configuration"],
        y=df["Runtime (s)"],
        xlabel="Эксперимент",
        ylabel="Время (сек)",
        title="Сравнение времени",
        colors=colors
    )
    
    # памятб
    st.subheader("Сравнение памяти(MiB)")
    plot_matplotlib_bar(
        x=df["Configuration"],
        y=df["Memory (MiB)"],
        xlabel="Эксперимент",
        ylabel="Память (MiB)",
        title="Сравнение памяти",
        colors=colors
    )
    
    # Сравнение Speedup
    st.subheader("Ускорение")
    speedup_df = calculate_speedups(df)
    plot_matplotlib_bar(
        x=speedup_df["Nodes"],
        y=speedup_df["Speedup"],
        xlabel="Кол-во нод",
        ylabel="Ускрение (в раз)",
        title="Оптимизированный vs Базовый вариант",
        colors=['#2ca02c', '#2ca02c']  # Зеленый для speedup
    )

if __name__ == "__main__":
    main()
