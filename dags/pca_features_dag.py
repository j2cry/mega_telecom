import sys
import pathlib
sys.path.append(pathlib.Path().joinpath('dags', 'megafon').as_posix())

import common
from datetime import datetime
from airflow import DAG
# from airflow.decorators import task
# from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor


with DAG('PCA_features', description='Geekbrains+Megafon DataScience course (prepare features)',
         schedule_interval=None, catchup=False, default_args=common.args) as dag:
    # refresh imports
    sys.path.append(common.path['dag'].as_posix())
    from jobs.source import compress_features

    # tasks
    raw_feats_waiting = FileSensor(
        task_id='waiting_for_raw_features',
        filepath=common.path['raw_features'].as_posix(),
        fs_conn_id='fs_default'
    )

    # compress_feats = SparkSubmitOperator(
    #     task_id='compress_features',
    #     conn_id='spark_default',
    #     application=f"{path['jobs'].joinpath('pca_compress.py').as_posix()} "
    #                 f"{path['input_features'].as_posix()} "     # input filename
    #                 f"{path['temp'].as_posix()}",               # output filename
    # )

    compress_feats = PythonOperator(          # THIS FOR DEBUG ONLY
        task_id='compress_features_with_PCA',
        python_callable=compress_features,
        op_args=[common.path['raw_features'].as_posix(),    # features_path
                 common.path['model_params'].as_posix(),    # params_path
                 common.path['temp'].as_posix(),            # target_path
                 ]
    )

    move_feats = BashOperator(
        task_id='move_features',
        bash_command=f"mv {common.path['temp'].as_posix() + '/*.csv'} {common.path['pca_features'].as_posix()};"
                     f"rm -rf {common.path['temp'].as_posix()}"
    )

    # tasks order
    raw_feats_waiting >> compress_feats >> move_feats
