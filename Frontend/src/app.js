import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import Sidebar from "./components/Sidebar";
import "./App.css";

const App = () => {
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [theme, setTheme] = useState("dark");
  const chatContainerRef = useRef(null);
  const apiUrl = "http://localhost:8000";
  const [userId, setUserId] = useState("");

  // Generate or retrieve user ID on component mount
  useEffect(() => {
    let storedId = localStorage.getItem("userId");
    if (!storedId) {
      storedId = uuidv4(); // Generate new UUID
      localStorage.setItem("userId", storedId);
    }
    setUserId(storedId);
  }, []);

  // Fetch initial chat history when userId is available
  useEffect(() => {
    if (!userId) return; // Prevent running if userId is not set yet

    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${apiUrl}/history/${userId}`);
        setMessages(
          response.data.history.map((item) => {
            const [role, ...contentParts] = item.message.split(": ");
            const content = contentParts.join(": "); // Ensures message is split correctly
            return { role, content, timestamp: item.timestamp };
          })
        );
      } catch (error) {
        console.error("Error fetching history:", error);
      }
    };

    fetchHistory();
  }, [userId]); // Depend on userId

  // Auto-scroll chat container when messages update
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isProcessing]);

  const handleSend = async (message) => {
    if (!message.trim()) return;

    const userMessage = { role: "You", content: message, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      const response = await axios.post(`${apiUrl}/chat`, { user_id: userId, message });
      const aiMessage = { role: "Teacher", content: response.data.response, timestamp: response.data.timestamp };
      setMessages((prev) => [...prev, aiMessage]);

      // Play pronunciation audio if included in response
      if (response.data.response.includes("/static/pronunciation.mp3")) {
        const audio = new Audio(`${apiUrl}/static/pronunciation.mp3`);
        audio.play();
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        { role: "Teacher", content: "Error processing your request.", timestamp: new Date().toISOString() },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      await axios.delete(`${apiUrl}/history/${userId}`);
      setMessages([]);
    } catch (error) {
      console.error("Error clearing history:", error);
    }
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
    document.body.classList.toggle("light-theme"); // Ensure theme updates properly
  };

  return (
    <div className={`app ${theme}`}>
      <Sidebar history={messages} onClear={handleClearHistory} onToggleTheme={toggleTheme} theme={theme} />
      <div className="main-content">
        <header className="header">
          <h1>German Buddy</h1>
        </header>
        <main className="chat-container" ref={chatContainerRef}>
          {messages.map((msg, index) => (
            <ChatMessage key={index} role={msg.role} content={msg.content} timestamp={msg.timestamp} />
          ))}
          {isProcessing && <ChatMessage role="Teacher" content="Typing..." isProcessing />}
        </main>
        <ChatInput onSend={handleSend} disabled={isProcessing} />
      </div>
    </div>
  );
};

export default App;
