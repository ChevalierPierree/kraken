from datetime import datetime, timedelta

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG

# Image publiée par la CI, épinglée par le SHA d'un commit de main
IMAGE = "ghcr.io/chevalierpierree/kraken-bootstrap:d753a65fee02edbdf19b6b1138dc4541c599fe60"

with DAG(
    dag_id="kraken_bootstrap",
    # Tous les jours à 6h00 UTC (minute, heure, jour, mois, jour de la semaine)
    schedule="0 6 * * *",
    start_date=datetime(2026, 11, 1),
    # Ne pas lancer un run pour chaque jour passé depuis start_date
    catchup=False,
    # En cas d'échec : 2 nouvelles tentatives, 5 minutes d'écart
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["kraken"],
):
    # Une seule tâche : lancer l'image, comme un docker run
    DockerOperator(
        task_id="run_job",
        image=IMAGE,
        # Au-delà de 30 minutes, la tâche est considérée en échec
        execution_timeout=timedelta(minutes=30),
        # Airflow tourne dans un conteneur : son dossier temporaire n'existe pas sur la machine
        mount_tmp_dir=False,
        # Le conteneur du job est supprimé quand il se termine
        auto_remove="success",
    )
