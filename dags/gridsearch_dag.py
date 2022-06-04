import settings
from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonVirtualenvOperator


with DAG('grid_search', description='Geekbrains+Megafon DataScience course (search for best parameters)',
         schedule_interval=None, catchup=False, default_args=settings.args) as dag:
    from dags.jobs.common import search_params_job

    # tasks
    grid_waiting = FileSensor(
        task_id='waiting_for_grid_parameters',
        filepath=settings.paths['grid'],
        fs_conn_id='fs_default'
    )

    train_waiting = FileSensor(
        task_id='waiting_for_train_data',
        filepath=settings.paths['train'],
        fs_conn_id='fs_default'
    )

    pca_feats_waiting = FileSensor(
        task_id='waiting_for_pca_features',
        filepath=settings.paths['pca_features'],
        fs_conn_id='fs_default'
    )

    model_parameters_waiting = FileSensor(
        task_id='waiting_for_model_parameters',
        filepath=settings.paths['model_params'],
        fs_conn_id='fs_default'
    )

    fit_parameters_waiting = FileSensor(
        task_id='waiting_for_fit_parameters',
        filepath=settings.paths['fit_params'],
        fs_conn_id='fs_default'
    )

    grid_search = PythonVirtualenvOperator(
        system_site_packages=False,
        requirements=['numpy==1.21.6', 'pandas==1.4.2', 'scikit-learn==1.0.2',
                      'lightgbm==3.3.2'
                      ],
        python_version='3.9',
        task_id='grid_search',
        python_callable=search_params_job,
        op_args=[settings.paths, ]
    )

    # tasks
    [grid_waiting, train_waiting, pca_feats_waiting, model_parameters_waiting, fit_parameters_waiting] >> grid_search
