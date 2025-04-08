import os
import time
import json
# import logging
import subprocess

def copy_to_hdfs():
    #складываем файл в hdfs
    subprocess.run(["docker", "exec", "namenode", "hdfs", "dfs", "-mkdir", "-p", "/input"])
    subprocess.run(["docker", "exec", "namenode", "hdfs", "dfs", "-put", "-f", "/podcasts.csv", "/input/"])

def run_spark_job(optimized=False):
    # запускаем Spark_application.py
    cmd = [
        "docker", "exec", "spark",
        "spark-submit", "--master", "spark://spark:7077",
        "/app/Spark_application.py"
    ]
    if optimized:
        cmd.append("--opt")

    start = time.time()
    subprocess.run(cmd)
    end = time.time()
    return round(end - start, 2)

# Создаем папку для результатов, чтобы не путаться
def create_results_dir(): 
    if not os.path.exists("results"):
        os.makedirs("results")

# статитика по памяти
def get_container_memory(container_name="spark"):
    result = subprocess.run(
        ["docker", "stats", "--no-stream", "--format", "{{.Name}}: {{.MemUsage}}"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if container_name in line:
            mem_raw = line.split(":")[1].strip().split("/")[0].strip()
            return mem_raw
    return "0MiB"

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.StreamHandler()
#     ]
# )


# запуск
def run_cluster(compose_file, label_prefix):
    # logger = logging.getLogger(__name__)
    subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"])
    # logger.info("Docker-compose up done, waiting to go out of safe mode")
    # print('Docker-compose up done, waiting to go out of safe mode') #просто для проверки, что грузится
    time.sleep(60) # если убираем, то возникает ошибка

    copy_to_hdfs()
    # logger.info("Загрузили данные в hdfs")
    create_results_dir()

    # Обычный запуск
    runtime_norm = run_spark_job(optimized=False)
    mem_norm = get_container_memory()
    with open(f"results/metrics_{label_prefix}.json", "w") as f: # .lower().replace(' ', '_')
        json.dump({
            "cluster": label_prefix,
            "optimized": False,
            "runtime_sec": runtime_norm,
            "mem_used": mem_norm,
            "timestamp": time.ctime()
        }, f, indent=2)


    # Оптимизированный запуск
    runtime_opt = run_spark_job(optimized=True)
    mem_opt = get_container_memory()
    with open(f"results/metrics_{label_prefix}_opt.json", "w") as f: #.lower().replace(' ', '_')
        json.dump({
            "cluster": label_prefix,
            "optimized": True,
            "runtime_sec": runtime_opt,
            "mem_used": mem_opt,
            "timestamp": time.ctime()
        }, f, indent=2)

    subprocess.run(["docker-compose", "-f", compose_file, "down"]) # отключаем докер


if __name__ == "__main__":
    run_cluster("docker-compose.yaml", "1 DataNode")
    run_cluster("docker-compose_3dn.yaml", "3 DataNodes")

