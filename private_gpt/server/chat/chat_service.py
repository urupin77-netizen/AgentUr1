from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterable

from injector import inject, singleton
from llama_index.core.chat_engine import ContextChatEngine, SimpleChatEngine
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.indices.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.postprocessor import SentenceTransformerRerank, SimilarityPostprocessor
from llama_index.core.storage import StorageContext
from llama_index.core.types import TokenGen
from pydantic import BaseModel
import logging

from private_gpt.components.embedding.embedding_component import EmbeddingComponent
from private_gpt.components.llm.llm_component import LLMComponent
from private_gpt.components.node_store.node_store_component import NodeStoreComponent
from private_gpt.components.vector_store.vector_store_component import VectorStoreComponent
from private_gpt.open_ai.extensions.context_filter import ContextFilter
from private_gpt.server.chunks.chunks_service import Chunk
from private_gpt.settings.settings import Settings
from private_gpt.components.reflection.reflection_component import ReflectionComponent
from private_gpt.components.hypothesis.hypothesis_component import HypothesisComponent

if TYPE_CHECKING:
    from llama_index.core.postprocessor.types import BaseNodePostprocessor

logger = logging.getLogger(__name__)


class Completion(BaseModel):
    response: str
    sources: list[Chunk] | None = None


class CompletionGen(BaseModel):
    response: TokenGen
    sources: list[Chunk] | None = None


@dataclass
class ChatEngineInput:
    system_message: ChatMessage | None = None
    last_message: ChatMessage | None = None
    chat_history: list[ChatMessage] | None = None

    @classmethod
    def from_messages(cls, messages: list[ChatMessage]) -> "ChatEngineInput":
        system_message = (
            messages[0] if len(messages) > 0 and messages[0].role == MessageRole.SYSTEM else None
        )
        last_message = messages[-1] if len(messages) > 0 and messages[-1].role == MessageRole.USER else None
        if system_message:
            messages.pop(0)
        if last_message:
            messages.pop(-1)
        chat_history = messages if len(messages) > 0 else None
        return cls(system_message=system_message, last_message=last_message, chat_history=chat_history)


@singleton
class ChatService:
    settings: Settings

    @inject
    def __init__(
        self,
        settings: Settings,
        llm_component: LLMComponent,
        vector_store_component: VectorStoreComponent,
        embedding_component: EmbeddingComponent,
        node_store_component: NodeStoreComponent,
        reflection_component: ReflectionComponent,
        hypothesis_component: HypothesisComponent,
    ) -> None:
        self.settings = settings
        self.llm_component = llm_component
        self.embedding_component = embedding_component
        self.vector_store_component = vector_store_component
        self.reflection = reflection_component
        self.hypothesis = hypothesis_component
        self.storage_context = StorageContext.from_defaults(
            vector_store=vector_store_component.vector_store,
            docstore=node_store_component.doc_store,
            index_store=node_store_component.index_store,
        )
        self.index = VectorStoreIndex.from_vector_store(
            vector_store_component.vector_store,
            storage_context=self.storage_context,
            llm=llm_component.llm,
            embed_model=embedding_component.embedding_model,
            show_progress=True,
        )

    def _chat_engine(
        self,
        system_prompt: str | None = None,
        use_context: bool = False,
        context_filter: ContextFilter | None = None,
    ) -> BaseChatEngine:
        settings = self.settings
        if use_context:
            vector_index_retriever = self.vector_store_component.get_retriever(
                index=self.index,
                context_filter=context_filter,
                similarity_top_k=self.settings.rag.similarity_top_k,
            )
            node_postprocessors: list["BaseNodePostprocessor"] = [
                MetadataReplacementPostProcessor(target_metadata_key="window"),
            ]
            if settings.rag.similarity_value:
                node_postprocessors.append(
                    SimilarityPostprocessor(similarity_cutoff=settings.rag.similarity_value)
                )
            if settings.rag.rerank.enabled:
                rerank_postprocessor = SentenceTransformerRerank(
                    model=settings.rag.rerank.model, top_n=settings.rag.rerank.top_n
                )
                node_postprocessors.append(rerank_postprocessor)

            return ContextChatEngine.from_defaults(
                system_prompt=system_prompt,
                retriever=vector_index_retriever,
                llm=self.llm_component.llm,
                node_postprocessors=node_postprocessors,
            )
        else:
            return SimpleChatEngine.from_defaults(system_prompt=system_prompt, llm=self.llm_component.llm)

    # -------- helpers for reflection --------
    @staticmethod
    def _chunks_to_sources(chunks: list[Chunk] | None) -> list[dict[str, Any]] | None:
        if not chunks:
            return None
        out: list[dict[str, Any]] = []
        for c in chunks[:4]:
            meta = c.document.doc_metadata if c.document and c.document.doc_metadata else {}
            out.append(
                {
                    "file": meta.get("file_name"),
                    "page": meta.get("page_label"),
                    "text": c.text[:500] if c.text else None,
                }
            )
        return out

    def _reflect_async_safe(
        self,
        *,
        system_prompt: str | None,
        last_user_message: str,
        chat_history: list[ChatMessage] | None,
        assistant_response: str,
        sources: list[dict[str, Any]] | None,
    ) -> None:
        try:
            self.reflection.reflect(
                system_prompt=system_prompt,
                last_user_message=last_user_message or "",
                chat_history=chat_history or [],
                assistant_response=assistant_response or "",
                sources=sources,
            )
        except Exception as e:  # noqa: BLE001
            logger.error("Reflection failed: %s", e)

    def stream_chat(
        self,
        messages: list[ChatMessage],
        use_context: bool = False,
        context_filter: ContextFilter | None = None,
    ) -> CompletionGen:
        chat_engine_input = ChatEngineInput.from_messages(messages)
        last_message_text = chat_engine_input.last_message.content if chat_engine_input.last_message else None
        system_prompt = chat_engine_input.system_message.content if chat_engine_input.system_message else None
        chat_history = chat_engine_input.chat_history if chat_engine_input.chat_history else None

        chat_engine = self._chat_engine(system_prompt=system_prompt, use_context=use_context, context_filter=context_filter)
        streaming_response = chat_engine.stream_chat(
            message=last_message_text if last_message_text is not None else "", chat_history=chat_history
        )
        sources_chunks = [Chunk.from_node(n) for n in streaming_response.source_nodes]
        sources = self._chunks_to_sources(sources_chunks)

        # Обертка генератора: после завершения — триггер рефлексии
        token_gen = streaming_response.response_gen

        def wrapped() -> TokenGen:
            full: str = ""
            for token in token_gen:
                # накапливаем текст, но отдаём токены как есть
                try:
                    if isinstance(token, str):
                        full += token
                    else:
                        delta = getattr(token, "delta", None)
                        if delta:
                            full += str(delta)
                        else:
                            msg = getattr(token, "message", None)
                            if msg and getattr(msg, "content", None):
                                full += str(msg.content)
                except Exception:  # noqa: BLE001
                    pass
                yield token
            # по окончании стрима — рефлексия
            self._reflect_async_safe(
                system_prompt=system_prompt,
                last_user_message=last_message_text or "",
                chat_history=chat_history or [],
                assistant_response=full,
                sources=sources,
            )

            # авто-гипотеза при низкой уверенности
            try:
                if getattr(self.settings, "hypothesis", None) and self.settings.hypothesis.auto_generate:
                    threshold = float(self.settings.hypothesis.auto_threshold)
                    refl_last = self.reflection.latest()  # type: ignore[attr-defined]
                    if refl_last and refl_last.confidence < threshold:
                        self.hypothesis.generate(
                            last_user_message=last_message_text or "",
                            assistant_response=full,
                            reflection=refl_last,  # type: ignore[arg-type]
                            top_memory_limit=5,
                            tags=["auto"],
                        )
            except Exception as e:
                logger.error("Auto-hypothesis failed: %s", e)

        completion_gen = CompletionGen(response=wrapped(), sources=sources_chunks)
        return completion_gen

    def chat(
        self,
        messages: list[ChatMessage],
        use_context: bool = False,
        context_filter: ContextFilter | None = None,
    ) -> Completion:
        chat_engine_input = ChatEngineInput.from_messages(messages)
        last_message_text = chat_engine_input.last_message.content if chat_engine_input.last_message else None
        system_prompt = chat_engine_input.system_message.content if chat_engine_input.system_message else None
        chat_history = chat_engine_input.chat_history if chat_engine_input.chat_history else None

        chat_engine = self._chat_engine(system_prompt=system_prompt, use_context=use_context, context_filter=context_filter)
        wrapped_response = chat_engine.chat(message=last_message_text if last_message_text is not None else "", chat_history=chat_history)
        sources_chunks = [Chunk.from_node(node) for node in wrapped_response.source_nodes]
        sources = self._chunks_to_sources(sources_chunks)
        completion_text = wrapped_response.response

        # Синхронная рефлексия
        self._reflect_async_safe(
            system_prompt=system_prompt,
            last_user_message=last_message_text or "",
            chat_history=chat_history or [],
            assistant_response=completion_text or "",
            sources=sources,
        )

        # --- авто-гипотеза, если включено и низкая уверенность ---
        try:
            if getattr(self.settings, "hypothesis", None) and self.settings.hypothesis.auto_generate:
                threshold = float(self.settings.hypothesis.auto_threshold)
                # последняя рефлексия уже сохранена ReflectionComponent-ом;
                # достанем её напрямую:
                from private_gpt.components.reflection.reflection_component import ReflectionComponent as RC
                refl_last = self.reflection.latest()  # type: ignore[attr-defined]
                if refl_last and refl_last.confidence < threshold:
                    self.hypothesis.generate(
                        last_user_message=last_message_text or "",
                        assistant_response=completion_text or "",
                        reflection=refl_last,  # type: ignore[arg-type]
                        top_memory_limit=5,
                        tags=["auto"],
                    )
        except Exception as e:
            logger.error("Auto-hypothesis failed: %s", e)

        completion = Completion(response=completion_text, sources=sources_chunks)
        return completion
