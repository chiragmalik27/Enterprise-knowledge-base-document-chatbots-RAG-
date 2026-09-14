import os

from dotenv import load_dotenv

from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

load_dotenv()


class QdrantStorage:

    def __init__(
        self,
        collection="docs",
        dim=3072
    ):

        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=30
        )

        self.collection = collection


        # Create collection if it doesn't exist
        if not self.client.collection_exists(
            self.collection
        ):

            self.client.create_collection(
                collection_name=self.collection,

                vectors_config=VectorParams(
                    size=dim,
                    distance=Distance.COSINE
                )
            )


        # Create index for source field
        self.client.create_payload_index(
            collection_name=self.collection,
            field_name="source",
            field_schema=PayloadSchemaType.KEYWORD,
            wait=True
        )


    # --------------------------------
    # UPSERT DATA
    # --------------------------------

    def upsert(self, ids, vectors, payloads):

        points = [
            PointStruct(
                id=ids[i],
                vector=vectors[i],
                payload=payloads[i]
            )
            for i in range(len(ids))
        ]

        self.client.upsert(
            collection_name=self.collection,
            points=points
        )


    # --------------------------------
    # SEARCH
    # --------------------------------

    def search(self, query_vector, top_k: int = 5):

        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            with_payload=True,
            limit=top_k
        ).points

        contexts = []
        sources = set()

        for r in results:

            payload = getattr(r, "payload", None) or {}

            text = payload.get("text", "")
            source = payload.get("source", "")

            if text:
                contexts.append(text)

            if source:
                sources.add(source)

        return {
            "contexts": contexts,
            "sources": list(sources)
        }


    # --------------------------------
    # DELETE PDF BY SOURCE
    # --------------------------------

    def delete_by_source(self, source):

        self.client.delete(
            collection_name=self.collection,

            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source",

                        match=MatchValue(
                            value=source
                        )
                    )
                ]
            ),

            wait=True
        )