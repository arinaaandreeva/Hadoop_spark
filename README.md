# Hadoop Spark
## To run
**Spark Application**
   
    python runner.py
    
**Visualization**   
    
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
       
 
    
