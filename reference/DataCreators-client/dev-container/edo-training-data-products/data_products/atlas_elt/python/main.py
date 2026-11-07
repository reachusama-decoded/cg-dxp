from pyspark.sql import SparkSession


def get_spark() -> SparkSession:
    try:
        from databricks.connect import DatabricksSession
        return DatabricksSession.builder.getOrCreate()
    except ImportError:
        return SparkSession.builder.getOrCreate()


def main() -> None:
    spark = get_spark()
    spark.sql("select current_timestamp() as generated_at").show(truncate=False)


if __name__ == "__main__":
    main()
