import React from 'react';

const ChatMessage = ({ role, content, timestamp, isProcessing }) => {
  const formattedTime = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

  return (
    <div className={`message-wrapper ${role === 'You' ? 'user-message-wrapper' : 'ai-message-wrapper'}`}>
      <div className={`${role === 'You' ? 'user-message' : 'ai-message'} ${isProcessing ? 'processing' : ''}`}>
        <div className="message-content">{content}</div>
        {!isProcessing && timestamp && <div className="timestamp">{formattedTime}</div>}
      </div>
    </div>
  );
};

export default ChatMessage;