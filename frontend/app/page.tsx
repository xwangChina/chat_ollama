"use client";

import { useEffect, useMemo, useState } from "react";
import ChatWindow from "../components/ChatWindow";
import Sidebar, {
  ChatSessionSummary,
  ProjectSummary
} from "../components/Sidebar";
import styles from "./page.module.css";
import { generateId } from "../lib/id";

type ProjectResponse = {
  projects: ProjectSummary[];
};

type ChatHistoryResponse = {
  chats: ChatSessionSummary[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function fetchProjects(): Promise<ProjectSummary[]> {
  const response = await fetch(`${API_BASE}/projects`);
  if (!response.ok) {
    return [];
  }

  const data: ProjectResponse = await response.json();
  return data.projects;
}

async function fetchChats(): Promise<ChatSessionSummary[]> {
  const response = await fetch(`${API_BASE}/chats`);
  if (!response.ok) {
    return [];
  }

  const data: ChatHistoryResponse = await response.json();
  return data.chats;
}

export default function Home() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [chats, setChats] = useState<ChatSessionSummary[]>([]);
  const [activeChatId, setActiveChatId] = useState<string>(() => generateId());

  useEffect(() => {
    fetchProjects().then(setProjects).catch(console.error);
    fetchChats()
      .then((data) => {
        setChats(data);
        if (data.length > 0) {
          setActiveChatId(data[0].id);
        }
      })
      .catch(console.error);
  }, []);

  const activeChat = useMemo(() => chats.find((chat) => chat.id === activeChatId), [
    chats,
    activeChatId
  ]);

  const handleCreateChat = () => {
    const newChat: ChatSessionSummary = {
      id: generateId(),
      title: "Untitled chat",
      updatedAt: new Date().toISOString()
    };
    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  return (
    <main className={styles.container}>
      <Sidebar
        projects={projects}
        chats={chats}
        selectedChatId={activeChatId}
        onSelectChat={setActiveChatId}
        onCreateChat={handleCreateChat}
      />
      <section className={styles.chatArea}>
        <header className={styles.chatHeader}>
          <h1>{activeChat?.title ?? "New conversation"}</h1>
          <p>Connect to your local Ollama and MCP tools seamlessly.</p>
        </header>
        <ChatWindow chatId={activeChatId} />
      </section>
    </main>
  );
}
