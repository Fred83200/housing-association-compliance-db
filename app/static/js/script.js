 function sendMessage() {
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;
      appendMsg(text, 'user');
      input.value = '';
      document.getElementById('chips').style.display = 'none';
      setTimeout(() => {
        const key = text.toLowerCase().replace(/[?!.]/g, '').trim();
        const resp = mockResponses[key] ||
          `I searched across all property records and documents for "<strong>${text}</strong>".<br><br>
          Found <strong>3 relevant results</strong> combining database records and document matches.
          Would you like me to compile a full case file or filter by a specific property?`;
        appendMsg(resp, 'bot');
      }, 800);
    }

    function appendMsg(html, role) {
      const container = document.getElementById('chat-messages');
      const div = document.createElement('div');
      div.className = 'app-chat-msg' + (role === 'user' ? ' app-chat-msg--user' : '');
      const initials = role === 'user' ? 'SB' : 'AI';
      const avClass = role === 'user' ? 'app-chat-avatar--user' : 'app-chat-avatar--bot';
      div.innerHTML = `<div class="app-chat-avatar ${avClass}">${initials}</div>
                       <div class="app-chat-bubble app-chat-bubble--${role}">${html}</div>`;
      container.appendChild(div);
      container.scrollTop = container.scrollHeight;
    }

    function sendChip(el) {
      document.getElementById('chat-input').value = el.textContent.trim();
      sendMessage();
    }

    function handleKey(e) {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    }

    function clearChat() {
      document.getElementById('chat-messages').innerHTML = `
        <div class="app-chat-msg">
          <div class="app-chat-avatar app-chat-avatar--bot">AI</div>
          <div class="app-chat-bubble app-chat-bubble--bot">
            Hello Sarah. I can search across all property records, compliance data, repair history, and documents. What would you like to know?
          </div>
        </div>`;
      document.getElementById('chips').style.display = 'flex';
    }

    function openForm() {
  document.getElementById("myForm").style.display = "block";
}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
}

    // ── Screen navigation ──────────────────────────
    function showScreen(id) {
      document.querySelectorAll('.app-screen').forEach(s => s.classList.remove('app-screen--active'));
      const el = document.getElementById('screen-' + id);
      if (el) el.classList.add('app-screen--active');

      document.querySelectorAll('#nav-list .govuk-service-navigation__item').forEach(item => {
        item.classList.remove('govuk-service-navigation__item--active');
        if (item.dataset.screen === id) item.classList.add('govuk-service-navigation__item--active');
      });

      window.scrollTo(0, 0);
    }

      function openChat() {
    document.getElementById("chatPopup").style.display = "block";
  }
      function startChat() {
        document.getElementById('chatStartScreen').style.display = 'none';
        document.getElementById('chatScreen').style.display = 'block';
      }
  function closeChat() {
    document.getElementById("chatPopup").style.display = "none";
  }

  function openResultsModal(title, html) {
    document.getElementById('resultsModalTitle').textContent = title;
    document.getElementById('resultsModalBody').innerHTML = html;
    document.getElementById('resultsModal').style.display = 'block';
  }

  function closeResultsModal() {
    document.getElementById('resultsModal').style.display = 'none';
  }

function openStairsRequestModal() {
  document.getElementById('stairsRequestModal').style.display = 'block';
}

function closeStairsRequestModal() {
  document.getElementById('stairsRequestModal').style.display = 'none';
}

function openComplianceModal() {
  document.getElementById('complianceModal').style.display = 'block';
}

function closeComplianceModal() {
  document.getElementById('complianceModal').style.display = 'none';
}

