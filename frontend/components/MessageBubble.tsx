"use client";

import styles from "./MessageBubble.module.css";

export interface Message {
  id: string;
  author: "user" | "assistant";
  content: string;
  createdAt: string;
  error?: boolean;
}

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.author === "user";

  return (
    <article
      className={
        isUser
          ? `${styles.bubble} ${styles.userBubble}`
          : `${styles.bubble} ${styles.assistantBubble}`
      }
    >
      <header className={styles.header}>
        <span className={styles.author}>{isUser ? "You" : "Assistant"}</span>
        <time dateTime={message.createdAt} className={styles.timestamp}>
          {new Date(message.createdAt).toLocaleTimeString()}
        </time>
      </header>
      <p className={message.error ? `${styles.content} ${styles.error}` : styles.content}>
        {message.content}
      </p>
    </article>
  );
}
