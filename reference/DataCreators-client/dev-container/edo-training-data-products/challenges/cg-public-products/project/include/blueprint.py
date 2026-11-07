"""AUTHOR lane O: reusable independently configured DAG factory.

The factory takes injected DAG/operator classes for local topology tests. In Astro,
those arguments are omitted and Airflow 3 classes are imported. Each config has
its own dag_id, relation_prefix, batch_id, connection_id and phase flags. Include
runtime.product.REQUIRED_TAGS in each DAG's tags; the shared Airflow rejects DAGs without them.
"""
def build_blueprint(config, dag_class=None, task_class=None):
    # AUTHOR: validate config, avoid shared mutable state, wire task dependencies/gate/callback.
    raise NotImplementedError('Complete the reusable blueprint')
