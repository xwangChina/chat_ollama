"use client";

import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import styles from "./ChatWindow.module.css";
import { fetchChatMessages, postChatCompletion, uploadFiles } from "../lib/api";
import { generateId } from "../lib/id";
import MessageBubble, { Message } from "./MessageBubble";

type UploadState = {
  files: File[];
  isUploading: boolean;
  error?: string;
};

export interface ChatWindowProps {
  chatId: string;
}

export default function ChatWindow({ chatId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [uploadState, setUploadState] = useState<UploadState>({ files: [], isUploading: false });
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let isActive = true;
    setMessages([]);
    setUploadState({ files: [], isUploading: false });

    fetchChatMessages(chatId)
      .then((history) => {
        if (!isActive) return;
        const restored = history
          .filter((message) => message.author === "user" || message.author === "assistant")
          .map((message) => ({
            id: message.id,
            author: message.author,
            content: message.content,
            createdAt: message.createdAt
          }));
        setMessages(restored);
      })
      .catch((error) => {
        if (!isActive) return;
        console.error(error);
      });

    return () => {
      isActive = false;
    };
  }, [chatId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const nextFiles = Array.from(event.target.files ?? []);
    setUploadState((prev) => ({ ...prev, files: nextFiles }));
  }, []);

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (!input.trim()) return;

      const userMessage: Message = {
        id: generateId(),
        author: "user",
        content: input,
        createdAt: new Date().toISOString()
      };

      setMessages((prev) => [...prev, userMessage]);
      setInput("");

      try {
        let uploadedFileIds: string[] = [];
        if (uploadState.files.length > 0) {
          setUploadState((prev) => ({ ...prev, isUploading: true, error: undefined }));
          uploadedFileIds = await uploadFiles(chatId, uploadState.files);
          setUploadState({ files: [], isUploading: false });
        }

        const assistantMessage = await postChatCompletion(chatId, {
          message: userMessage.content,
          fileIds: uploadedFileIds
        });

        setMessages((prev) => [
          ...prev,
          {
            id: assistantMessage.id ?? generateId(),
            author: "assistant",
            content: assistantMessage.content ?? "(no content)",
            createdAt: assistantMessage.createdAt ?? new Date().toISOString()
          }
        ]);
      } catch (error) {
        console.error(error);
        setMessages((prev) => [
          ...prev,
          {
            id: generateId(),
            author: "assistant",
            content: "Sorry, something went wrong while contacting the backend.",
            createdAt: new Date().toISOString(),
            error: true
          }
        ]);
        setUploadState((prev) => ({ ...prev, isUploading: false, error: String(error) }));
      }
    },
    [chatId, input, uploadState.files]
  );

  return (
    <div className={styles.wrapper}>
      <div className={styles.history}>
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={bottomRef} />
      </div>

      <form className={styles.inputArea} onSubmit={handleSubmit}>
        <label className={styles.fileUpload}>
          <input type="file" multiple onChange={handleFileChange} />
          <span>Attach files</span>
        </label>

        <textarea
          className={styles.textarea}
          placeholder="Ask anything about your data..."
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={2}
          required
        />

        <button type="submit" className={styles.submitButton} disabled={!input.trim()}>
          Send
        </button>
      </form>

      {uploadState.files.length > 0 && (
        <div className={styles.fileList}>
          <strong>Ready to upload:</strong>
          <ul>
            {uploadState.files.map((file) => (
              <li key={file.name}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}
      {uploadState.isUploading && <p className={styles.status}>Uploading files…</p>}
      {uploadState.error && <p className={styles.error}>Upload failed: {uploadState.error}</p>}
    </div>
  );
}
