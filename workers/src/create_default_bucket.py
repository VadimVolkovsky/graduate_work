from cdn.src.minio_service import MinioService

if __name__ == "__main__":
    minio_service = MinioService()
    minio_service._check_bucket_exists()