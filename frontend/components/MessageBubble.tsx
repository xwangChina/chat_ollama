"use client";

import styles from "./MessageBubble.module.css";

export interface Message {
  id: string;
  author: "user" | "assistant";
  content: string;
  createdAt: string;
  error?: boolean;
  loading?: boolean;
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
      {message.loading ? (
        <div className={styles.typing} aria-label="Assistant is typing">
          <span className={styles.typingDot} />
          <span className={styles.typingDot} />
          <span className={styles.typingDot} />
        </div>
      ) : (
        <p className={message.error ? `${styles.content} ${styles.error}` : styles.content}>
          {message.content}
        </p>
      )}
    </article>
  );
}
