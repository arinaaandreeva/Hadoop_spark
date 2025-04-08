import sys
import time
import logging
import json
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import GBTRegressor

# логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('spark_job.log'), # d файл
        logging.StreamHandler() # печать во время выполнения
    ]
)

def run_spark_job(optimized=False):
    logger = logging.getLogger(__name__)
    start_time = time.time()
    
    spark = SparkSession.builder \
        .appName("SparkAnalysis") \
        .getOrCreate()
    
    logger.info("Начало выполнения Spark job")

    logger.info("Загрузка данных из HDFS")
    df = spark.read.csv("hdfs://namenode:9000/input/podcasts.csv", 
                       header=True, 
                       inferSchema=True)
    logger.info(f"Загружено {df.count()} строк")

    # Преобразование категориальных признаков
    logger.info("Преобразование категориальных признаков")
    indexers = [
        StringIndexer(inputCol="Genre", outputCol="GenreIndex"),
        StringIndexer(inputCol="Publication_Day", outputCol="DayIndex"),
        StringIndexer(inputCol="Publication_Time", outputCol="TimeIndex"),
        StringIndexer(inputCol="Episode_Sentiment", outputCol="SentimentIndex")
    ]

    encoders = [
        OneHotEncoder(inputCol="GenreIndex", outputCol="GenreVec"),
        OneHotEncoder(inputCol="DayIndex", outputCol="DayVec"),
        OneHotEncoder(inputCol="TimeIndex", outputCol="TimeVec"),
        OneHotEncoder(inputCol="SentimentIndex", outputCol="SentimentVec")
    ]

    assembler = VectorAssembler(
        inputCols=[
            "Host_Popularity", "Guest_Popularity", "Episode_Length",
            "Number_of_Ads", "GenreVec", "DayVec", "TimeVec", "SentimentVec"
        ],
        outputCol="features"
    )

    # Pipeline и трансформация данных
    pipeline = Pipeline(stages=indexers + encoders + [assembler])
    model = pipeline.fit(df)
    df_transformed = model.transform(df)

    if optimized:
        logger.info("Применение оптимизаций: repartition + persist")
        df_transformed = df_transformed.repartition(8).persist()
        df_transformed.count()  # что-то считаем

    logger.info("Разделение данных на train/test")
    train_data, test_data = df_transformed.randomSplit([0.8, 0.2], seed=123)
    
    logger.info("Обучение модели GBT") # небольшая модель
    gbt = GBTRegressor(
        featuresCol='features',
        labelCol='Listening_Time',
        seed=42,
        maxIter=5, 
        maxDepth=3,
        maxBins=32,
        subsamplingRate=0.8
    )
    
    model = gbt.fit(train_data)
    
    logger.info("Оценка модели")
    predictions = model.transform(test_data)
    evaluator = RegressionEvaluator(
        labelCol="Listening_Time",
        predictionCol="prediction",
        metricName="rmse"
    )
    rmse = evaluator.evaluate(predictions)
    
    # Замер памяти
    mem_used = spark.sparkContext.statusTracker().getExecutorInfos()[0].memoryUsed() / (1024 * 1024)
    
    # Логирование результатов
    runtime = time.time() - start_time
    logger.info(f"Время выполнения: {runtime:.2f} сек")
    logger.info(f"Использовано памяти: {mem_used:.2f} MiB")
    logger.info("Spark UI: http://localhost:9870")

    # сбор рез-тов
    result = {
        "runtime_sec": round(runtime, 2),
        "mem_used": f"{mem_used:.2f} MiB",
        "rmse": rmse,
        "optimized": optimized
    }
    print(json.dumps(result))

    spark.stop()

if __name__ == "__main__":
    optimized = "--optimized" in sys.argv
    run_spark_job(optimized=optimized)