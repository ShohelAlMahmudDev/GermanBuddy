import React from 'react';

const Sidebar = ({ history, onClear, onToggleTheme, theme }) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Chat History</h2>
      </div>
      <div className="history-list">
        {history.length === 0 ? (
          <p>No history yet.</p>
        ) : (
          history.map((msg, index) => (
            <div key={index} className="history-item">
              {msg.role === 'You' ? 'You: ' : 'Teacher: '}{msg.content.slice(0, 30)}{msg.content.length > 30 ? '...' : ''}
            </div>
          ))
        )}
      </div>
      <div className="sidebar-actions">
        <button onClick={onClear}>Clear History</button>
        <button onClick={onToggleTheme}>
          Switch to {theme === 'dark' ? 'Light' : 'Dark'} Mode
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;