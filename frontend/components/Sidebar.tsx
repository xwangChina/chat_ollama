"use client";

import { useMemo } from "react";
import styles from "./Sidebar.module.css";

export interface ProjectSummary {
  id: string;
  name: string;
  description?: string;
}

export interface ChatSessionSummary {
  id: string;
  title: string;
  updatedAt: string;
}

export interface SidebarProps {
  projects: ProjectSummary[];
  chats: ChatSessionSummary[];
  selectedChatId?: string;
  onSelectChat: (chatId: string) => void;
  onCreateChat: () => void;
}

export function Sidebar({
  projects,
  chats,
  selectedChatId,
  onSelectChat,
  onCreateChat
}: SidebarProps) {
  const sortedChats = useMemo(
    () =>
      [...chats].sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      ),
    [chats]
  );

  return (
    <aside className={styles.sidebar}>
      <div className={styles.header}>
        <h1 className={styles.title}>Ollama Workspace</h1>
        <p className={styles.subtitle}>Local AI copilots for your data</p>
        <button className={styles.newChatButton} onClick={onCreateChat}>
          + New chat
        </button>
      </div>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Projects</h2>
        <ul className={styles.list}>
          {projects.map((project) => (
            <li key={project.id} className={styles.listItem} title={project.description}>
              <span>{project.name}</span>
            </li>
          ))}
          {projects.length === 0 && <li className={styles.placeholder}>No projects yet</li>}
        </ul>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Recent Chats</h2>
        <ul className={styles.list}>
          {sortedChats.map((chat) => (
            <li
              key={chat.id}
              className={
                chat.id === selectedChatId
                  ? `${styles.listItem} ${styles.listItemActive}`
                  : styles.listItem
              }
              onClick={() => onSelectChat(chat.id)}
            >
              <span>{chat.title}</span>
              <small>{new Date(chat.updatedAt).toLocaleString()}</small>
            </li>
          ))}
          {sortedChats.length === 0 && (
            <li className={styles.placeholder}>Start a new conversation</li>
          )}
        </ul>
      </section>
    </aside>
  );
}

export default Sidebar;
