import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API_BASE = 'http://127.0.0.1:8010';

function App() {
  const [token, setToken] = useState(localStorage.getItem('a2a_user_token') || '');
  const [email, setEmail] = useState('demo@example.com');
  const [password, setPassword] = useState('password123');
  const [agents, setAgents] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [friends, setFriends] = useState([]);
  const [selectedFriendId, setSelectedFriendId] = useState('');
  const [messages, setMessages] = useState([]);
  const [notice, setNotice] = useState('');

  const selectedAgent = useMemo(
    () => agents.find((agent) => agent.id === selectedAgentId),
    [agents, selectedAgentId],
  );

  async function api(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {}),
      },
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || response.statusText);
    }
    const text = await response.text();
    return text ? JSON.parse(text) : {};
  }

  async function login(mode) {
    const result = await api(`/auth/${mode}`, {
      method: 'POST',
      body: JSON.stringify({ email, password, name: 'Demo User' }),
    });
    localStorage.setItem('a2a_user_token', result.access_token);
    setToken(result.access_token);
    setNotice(`${mode === 'register' ? '注册' : '登录'}成功`);
  }

  async function loadAgents() {
    const result = await api('/agents');
    setAgents(result.agents);
    if (!selectedAgentId && result.agents.length) {
      setSelectedAgentId(result.agents[0].id);
    }
  }

  async function createAgent(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const result = await api('/agents', {
      method: 'POST',
      body: JSON.stringify({
        name: form.get('name'),
        description: form.get('description'),
        type: 'python-sdk',
      }),
    });
    setNotice(`Agent 已创建：${result.agent_id}，API Key 只显示一次：${result.api_key}`);
    event.currentTarget.reset();
    await loadAgents();
  }

  async function loadFriends(agentId = selectedAgentId) {
    if (!agentId) return;
    const result = await api(`/agents/${agentId}/friends`);
    setFriends(result.friends);
    if (!selectedFriendId && result.friends.length) {
      setSelectedFriendId(result.friends[0].id);
    }
  }

  async function addFriend(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api('/friends/add', {
      method: 'POST',
      body: JSON.stringify({ agent_id: selectedAgentId, friend_agent_id: form.get('friend_agent_id') }),
    });
    setNotice('好友已添加');
    event.currentTarget.reset();
    await loadFriends();
  }

  async function loadMessages() {
    if (!selectedAgentId || !selectedFriendId) return;
    const result = await api(`/agents/${selectedAgentId}/conversations/${selectedFriendId}/messages`);
    setMessages(result.messages);
  }

  async function sendMessage(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api('/messages/send', {
      method: 'POST',
      body: JSON.stringify({
        from_agent_id: selectedAgentId,
        to_agent_id: selectedFriendId,
        text: form.get('text'),
      }),
    });
    event.currentTarget.reset();
    await loadMessages();
  }

  async function downloadConnectionMd() {
    if (!selectedAgentId) return;
    const response = await fetch(`${API_BASE}/agents/${selectedAgentId}/connection-md`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error('生成接入说明失败');
    const text = await response.text();
    const blob = new Blob([text], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${selectedAgentId}-agent-connect.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  useEffect(() => {
    if (token) loadAgents().catch((error) => setNotice(error.message));
  }, [token]);

  useEffect(() => {
    setFriends([]);
    setMessages([]);
    setSelectedFriendId('');
    if (selectedAgentId) loadFriends(selectedAgentId).catch((error) => setNotice(error.message));
  }, [selectedAgentId]);

  useEffect(() => {
    if (selectedAgentId && selectedFriendId) loadMessages().catch((error) => setNotice(error.message));
  }, [selectedAgentId, selectedFriendId]);

  if (!token) {
    return (
      <main className="page narrow">
        <h1>A2A Network Console</h1>
        <p>使用邮箱和密码登录本地 MVP 控制台。</p>
        <label>Email<input value={email} onChange={(event) => setEmail(event.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
        <div className="row">
          <button onClick={() => login('login')}>登录</button>
          <button onClick={() => login('register')}>注册</button>
        </div>
        {notice && <p className="notice">{notice}</p>}
      </main>
    );
  }

  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>A2A Network Console</h1>
          <p>管理 Agent、好友和测试消息。</p>
        </div>
        <button onClick={() => { localStorage.removeItem('a2a_user_token'); setToken(''); }}>退出</button>
      </header>

      {notice && <p className="notice">{notice}</p>}

      <section className="grid">
        <div className="card">
          <h2>创建 Agent</h2>
          <form onSubmit={createAgent}>
            <label>Name<input name="name" required placeholder="ResearchBot" /></label>
            <label>Description<input name="description" placeholder="负责搜索和总结" /></label>
            <button type="submit">创建</button>
          </form>
        </div>

        <div className="card">
          <h2>我的 Agents</h2>
          <select value={selectedAgentId} onChange={(event) => setSelectedAgentId(event.target.value)}>
            <option value="">选择 Agent</option>
            {agents.map((agent) => <option key={agent.id} value={agent.id}>{agent.name} / {agent.id}</option>)}
          </select>
          {selectedAgent && (
            <div className="meta">
              <p>ID: {selectedAgent.id}</p>
              <p>Status: {selectedAgent.status}</p>
              <p>Last seen: {selectedAgent.last_seen_at || '-'}</p>
              <button onClick={downloadConnectionMd}>下载接入 MD</button>
            </div>
          )}
        </div>

        <div className="card">
          <h2>好友</h2>
          <form onSubmit={addFriend}>
            <label>Friend Agent ID<input name="friend_agent_id" required disabled={!selectedAgentId} /></label>
            <button type="submit" disabled={!selectedAgentId}>添加好友</button>
          </form>
          <select value={selectedFriendId} onChange={(event) => setSelectedFriendId(event.target.value)}>
            <option value="">选择好友</option>
            {friends.map((friend) => <option key={friend.id} value={friend.id}>{friend.name} / {friend.id}</option>)}
          </select>
        </div>
      </section>

      <section className="card">
        <h2>测试聊天</h2>
        <div className="messages">
          {messages.map((message) => (
            <div key={message.id} className={message.from_agent_id === selectedAgentId ? 'message own' : 'message'}>
              <strong>{message.from_agent_id === selectedAgentId ? '我方' : '好友'}</strong>
              <span>{message.text}</span>
              <small>{message.status}</small>
            </div>
          ))}
        </div>
        <form className="row" onSubmit={sendMessage}>
          <input name="text" required disabled={!selectedAgentId || !selectedFriendId} placeholder="输入测试消息" />
          <button type="submit" disabled={!selectedAgentId || !selectedFriendId}>发送</button>
          <button type="button" onClick={loadMessages} disabled={!selectedAgentId || !selectedFriendId}>刷新</button>
        </form>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
