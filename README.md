# Hadoop Spark
## 
**Spark Application**
   
    python runner.py
    
**Визуализация**   
    
    streamlit run streamlit_app.py  


## Files
     ├── docker-compose.yaml         # for 1 DataNode
     ├── docker-compose_3dn.yaml     # for 3 DataNode
     ├── hadoop.env                  # setting environment
          * HDFS_CONF_dfs_blocksize=67108864  # for limit blocksize
          * HDFS_CONF_dfs_replication=1       # number of replics
     ├── podcasts.csv                # data from https://www.kaggle.com/datasets/ysthehurricane/podcast-listening-time-prediction-dataset 
     ├── runner.py                   # for running docker and spark application
     ├── Spark_application.py        # spark application and optimization
     ├── streamlit_app.py            # dashboard with results
     ├── spark_job.log               # logs 
     ├── results                     # results for each experiment
     |   ├── metrics_1 DataNode.json 
     |   ├── ....
     ├── img                         # dashboard with results


### Cluster running
Можно проверить blocksize

Replication =  3 по умолчанию (если HDFS_CONF_dfs_replication=1 не установлено) . Если DataNode одна, то replication = 1.
![alt text](https://github.com/arinaaandreeva/Hadoop_spark/blob/master/img/Utilities.JPG)


### Dashboard with results
 - Несколько datanode позволяют не терять данные в случае поломки одного из них, так как у нас есть реплики.
 - Оптимизированное приложение работает быстрее, но использует больше ресурсов из-за replication, cach.

![alt text](https://github.com/arinaaandreeva/Hadoop_spark/blob/master/img/Streamlit1.JPG)
![alt text](https://github.com/arinaaandreeva/Hadoop_spark/blob/master/img/Streamlit2.JPG)
![alt text](https://github.com/arinaaandreeva/Hadoop_spark/blob/master/img/Streamlit3.JPG)
       
 
    
