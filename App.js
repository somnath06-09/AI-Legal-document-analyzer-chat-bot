import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [input, setInput] = useState("");

  const handleFileUpload = async () => {
    if (!file) return;
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://127.0.0.1:5000/analyze_file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessages(prev => [...prev, { user: `Uploaded: ${file.name}`, bot: res.data.response }]);
    } catch (error) {
      console.error("Upload error:", error);
      setMessages(prev => [...prev, { user: "File upload failed.", bot: "Something went wrong during analysis." }]);
    }

    setUploading(false);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { user: input, bot: "Analyzing..." };
    setMessages(prev => [...prev, userMsg]);

    try {
      const res = await axios.post("http://127.0.0.1:5000/ask_gemini", { message: input });
      const botReply = { user: input, bot: res.data.response };
      setMessages(prev => [...prev.slice(0, -1), botReply]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages(prev => [...prev, { user: input, bot: "Error retrieving response." }]);
    }

    setInput("");
  };

  return (
    <div className="min-h-screen bg-[#111827] text-gray-100 p-8 font-inter">
      <h1 className="text-4xl font-bold mb-8 text-center text-purple-300">AI Legal Document Analyzer</h1>

      <div className="mb-4 flex items-center gap-2">
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={(e) => setFile(e.target.files[0])}
          className="bg-[#1f2937] border border-[#374151] text-gray-300 px-4 py-2 rounded-md w-1/2"
        />
        <button
          className="bg-purple-600 text-white px-5 py-2 rounded-md hover:bg-purple-500 transition font-semibold"
          onClick={handleFileUpload}
          disabled={uploading || !file}
        >
          {uploading ? "Analyzing..." : "Upload & Analyze"}
        </button>
      </div>

      <div className="border border-[#374151] rounded-lg p-5 h-96 overflow-y-auto bg-[#1f2937] mb-6 shadow-inner">
        {messages.map((msg, idx) => (
          <div key={idx} className="mb-2">
            <p className="text-sm text-purple-400 font-medium">You:</p>
            <div className="ml-2 mb-3 text-gray-200 bg-[#1f2937] border border-[#374151] rounded-md p-3 text-sm shadow-sm">
              {msg.user}
            </div>
            <p className="text-sm text-green-400 font-medium">AI:</p>
            <div
              className="ml-2 mt-1 bg-[#111827] p-4 rounded-md border border-[#374151] text-sm leading-relaxed space-y-2 text-gray-100"
              dangerouslySetInnerHTML={{ __html: msg.bot }}
            />
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          className="flex-1 px-4 py-2 border border-[#374151] rounded-md bg-[#1f2937] text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
          type="text"
          placeholder="Ask about the document..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") sendMessage(); }}
        />
        <button
          className="bg-purple-600 text-white px-5 py-2 rounded-md hover:bg-purple-500 transition font-semibold"
          onClick={sendMessage}
          disabled={!input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
