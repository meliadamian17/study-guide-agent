from study_guide_agent.orchestrators.protocol import StudyGuideStorage
from study_guide_agent.storage.azure_blob import AzureBlobStorage
from study_guide_agent.storage.gcs import GCSStorage


def create_storage(provider: str) -> StudyGuideStorage:
    normalized = provider.strip().lower()
    if normalized == "azure":
        return AzureBlobStorage()
    if normalized == "gcs":
        return GCSStorage()
    raise ValueError(f"Unknown storage provider: {provider}")


__all__ = ["StudyGuideStorage", "AzureBlobStorage", "GCSStorage", "create_storage"]
