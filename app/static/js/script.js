const chatResponseStore = {};
async function sendMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();

  if (!text) return;

  appendMsg(escapeHtml(text), 'user');
  input.value = '';

  const chips = document.getElementById('chips');
  if (chips) chips.style.display = 'none';

  const chatIntro = document.getElementById('chat-intro');
  if (chatIntro) chatIntro.style.display = 'none';

  const loadingMessage = appendMsg('Searching live database and document evidence...', 'bot');

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text })
    });

    if (!response.ok) {
      throw new Error(`Chat API failed with status ${response.status}`);
    }

    const result = await response.json();

    const dataRows = Array.isArray(result.data) ? result.data : [];
    const hasTableData = dataRows.length > 0;

    if (hasTableData) {
      const modalTitle = buildModalTitle(text);
      const modalHtml = buildDetailedResponseHtml(result.answer, dataRows);
      const summaryText = buildChatSummary(text, dataRows);

        const responseId = createChatResponseId();

        chatResponseStore[responseId] = {
          title: modalTitle,
          html: modalHtml
        };

        replaceBotMessage(loadingMessage, `
          <p>${escapeHtml(summaryText)}</p>
          <button class="govuk-button govuk-button--secondary govuk-!-margin-bottom-0"
            onclick="openChatResultsModal('${responseId}')">
            View detailed response
          </button>
        `);

      return;
    }

    const answer = result.answer || 'No answer returned.';

    if (answer.length > 250) {
        const responseId = createChatResponseId();

        chatResponseStore[responseId] = {
          title: buildModalTitle(text),
          html: `
            <div class="app-ai-response">
              <div class="app-ai-response__summary">
                ${formatAiAnswer(answer)}
              </div>
            </div>
          `
        };

        replaceBotMessage(loadingMessage, `
          <p>I found a detailed response for your question.</p>
          <button class="govuk-button govuk-button--secondary govuk-!-margin-bottom-0"
            onclick="openChatResultsModal('${responseId}')">
            View detailed response
          </button>
        `);

        appendMsg(`
          <p>What would you like to check next?</p>
          ${renderFollowUpChips()}
        `, 'bot');

      return;
    }

    replaceBotMessage(loadingMessage, `
      <p>${escapeHtml(answer)}</p>
    `);

    appendMsg(`
      <p>What would you like to check next?</p>
      ${renderFollowUpChips()}
    `, 'bot');

  } catch (error) {
    console.error(error);
    replaceBotMessage(loadingMessage, 'Sorry, I could not connect to the backend API');
  }
}

function renderFollowUpChips() {
  return `
    <div class="app-chat-followups">
      <button type="button" class="app-chip" onclick="sendChip(this)">Which properties are non-compliant?</button>
      <button type="button" class="app-chip" onclick="sendChip(this)">Show overdue inspections</button>
      <button type="button" class="app-chip" onclick="sendChip(this)">Find all boiler repair records</button>
      <button type="button" class="app-chip" onclick="sendChip(this)">List open FOI requests</button>
      <button type="button" class="app-chip" onclick="sendChip(this)">Properties with damp issues</button>
    </div>
  `;
}

function createChatResponseId() {
  return `chat-response-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function openChatResultsModal(responseId) {
  const storedResponse = chatResponseStore[responseId];

  if (!storedResponse) return;

  openResultsModal(storedResponse.title, storedResponse.html);

  if (!storedResponse.followUpsShown) {
    const followUpMessage = appendMsg(`
      <p>What would you like to check next?</p>
      ${renderFollowUpChips()}
    `, 'bot');

    followUpMessage.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });

    storedResponse.followUpsShown = true;
  }
}

function buildChatSummary(question, rows) {
  const count = rows.length;
  const lowerQuestion = question.toLowerCase();

  if (lowerQuestion.includes('non-compliant') || lowerQuestion.includes('non compliant')) {
    return `${count} non-compliant propert${count === 1 ? 'y' : 'ies'} found.`;
  }

  if (lowerQuestion.includes('overdue')) {
    return `${count} overdue record${count === 1 ? '' : 's'} found.`;
  }

  if (lowerQuestion.includes('foi') || lowerQuestion.includes('stairs')) {
    return `${count} STAIRS / FOI request${count === 1 ? '' : 's'} found.`;
  }

  if (lowerQuestion.includes('boiler') || lowerQuestion.includes('repair')) {
    return `${count} repair record${count === 1 ? '' : 's'} found.`;
  }

  return `${count} result${count === 1 ? '' : 's'} found.`;
}

function buildModalTitle(question) {
  const lowerQuestion = question.toLowerCase();

  if (lowerQuestion.includes('non-compliant') || lowerQuestion.includes('non compliant')) {
    return 'Non-compliant properties';
  }

  if (lowerQuestion.includes('overdue')) {
    return 'Overdue records';
  }

  if (lowerQuestion.includes('foi') || lowerQuestion.includes('stairs')) {
    return 'STAIRS / FOI requests';
  }

  if (lowerQuestion.includes('boiler') || lowerQuestion.includes('repair')) {
    return 'Repair records';
  }

  return 'Detailed response';
}

function buildDetailedResponseHtml(answer, rows) {
  return `
    <div class="app-ai-response">

      <div class="app-ai-response__summary govuk-inset-text">
        ${rows.length} result${rows.length === 1 ? '' : 's'} found.
      </div>

      ${renderTable(rows)}

    </div>
  `;
}

function formatAiAnswer(answer) {
  if (!answer) return '<p>No summary returned.</p>';

  return escapeHtml(answer)
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>');
}

function appendMsg(html, role) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');

  div.className = 'app-chat-msg' + (role === 'user' ? ' app-chat-msg--user' : '');

  const initials = role === 'user' ? 'SB' : 'AI';
  const avatarClass = role === 'user' ? 'app-chat-avatar--user' : 'app-chat-avatar--bot';

  div.innerHTML = `
    <div class="app-chat-avatar ${avatarClass}">${initials}</div>
    <div class="app-chat-bubble app-chat-bubble--${role}">${html}</div>
  `;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;

  return div;
}

function replaceBotMessage(messageElement, html) {
  if (!messageElement) return;

  const bubble = messageElement.querySelector('.app-chat-bubble--bot');

  if (bubble) {
    bubble.innerHTML = html;
  }
}

function replaceLastBotMessage(html) {
  const botMessages = document.querySelectorAll('.app-chat-bubble--bot');
  const lastBotMessage = botMessages[botMessages.length - 1];

  if (lastBotMessage) {
    lastBotMessage.innerHTML = html;
  } else {
    appendMsg(html, 'bot');
  }
}

function renderTable(rows) {
  const columns = Object.keys(rows[0]);

  return `
    <table class="govuk-table">
      <thead class="govuk-table__head">
        <tr class="govuk-table__row">
          ${columns.map(col => `<th class="govuk-table__header">${escapeHtml(formatColumnName(col))}</th>`).join('')}
        </tr>
      </thead>
      <tbody class="govuk-table__body">
        ${rows.map(row => `
          <tr class="govuk-table__row">
            ${columns.map(col => `<td class="govuk-table__cell">${formatTableCell(col, row[col])}</td>`).join('')}
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

function renderObject(data) {
  return `<pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function formatValue(value) {
  if (value === null || value === undefined) return '—';
  return value;
}

function formatTableCell(column, value) {
  if (value === null || value === undefined) return '—';

  if (column === 'property_id') {
    return `
        <a class="govuk-link"
           href="#"
           onclick="showCaseFile(${Number(value)}); closeResultsModal(); return false;">
          ${escapeHtml(value)}
        </a>
    `;
  }

  if (column.includes('date')) {
    return escapeHtml(formatDisplayDate(value));
  }

  if (column === 'compliance_status') {
    let tagClass = 'govuk-tag--green';

    if (value === 'Non-Compliant') {
      tagClass = 'govuk-tag--red';
    }

    if (value === 'Inspection Due') {
      tagClass = 'govuk-tag--yellow';
    }

    return `<strong class="govuk-tag ${tagClass}">${escapeHtml(value)}</strong>`;
  }

  if (column === 'status') {
    return formatStatusTag(value);
  }

  return escapeHtml(formatValue(value));
}

function formatDisplayDate(value) {
  if (!value) return '—';

  const date = new Date(`${value}T00:00:00`);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
}

function formatStatusTag(value) {
  const status = String(value || '').toLowerCase();

  let tagClass = 'govuk-tag--grey';

  if (status === 'completed' || status === 'complete') {
    tagClass = 'govuk-tag--green';
  }

  if (status === 'in progress') {
    tagClass = 'govuk-tag--turquoise';
  }

  if (status === 'scheduled') {
    tagClass = 'govuk-tag--yellow';
  }

  if (status === 'reported' || status === 'open') {
    tagClass = 'govuk-tag--orange';
  }

  if (status === 'in review') {
    tagClass = 'govuk-tag--purple';
  }

  return `<strong class="govuk-tag ${tagClass}">${escapeHtml(value)}</strong>`;
}

function formatColumnName(column) {
  const mappings = {
    property_id: 'Property ID',
    repair_id: 'Repair ID',
    uprn: 'UPRN',
    address_line_1: 'Address',
    city: 'City',
    postcode: 'Postcode',
    compliance_status: 'Compliance status',
    last_inspection_date: 'Last inspection',
    repair_category: 'Repair category',
    reported_date: 'Reported',
    completed_date: 'Completed',
    contractor_name: 'Contractor',
    request_reference: 'Reference',
    request_type: 'Request type',
    request_date: 'Received',
    due_date: 'Due date',
    assigned_to: 'Assigned to',
    first_name: 'First name',
    last_name: 'Last name'
  };

  return mappings[column] || column.replaceAll('_', ' ');
}

function sendChip(el) {
  document.getElementById('chat-input').value = el.textContent.trim();
  sendMessage();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function clearChat() {
  document.getElementById('chat-messages').innerHTML = `
    <div class="app-chat-msg">
      <div class="app-chat-avatar app-chat-avatar--bot">AI</div>
      <div class="app-chat-bubble app-chat-bubble--bot">
        Hello Sarah. I can search across live property records, compliance data, repair history and documents. What would you like to know?
      </div>
    </div>`;

  const chips = document.getElementById('chips');
  if (chips) chips.style.display = 'flex';
}

function showScreen(id) {
  document.querySelectorAll('.app-screen').forEach(screen => {
    screen.classList.remove('app-screen--active');
  });

  const screen = document.getElementById('screen-' + id);
  if (screen) screen.classList.add('app-screen--active');

  document.querySelectorAll('#nav-list .govuk-service-navigation__item').forEach(item => {
    item.classList.remove('govuk-service-navigation__item--active');
    if (item.dataset.screen === id) {
      item.classList.add('govuk-service-navigation__item--active');
    }
  });

  window.scrollTo(0, 0);
}

function openChat() {
  document.getElementById('chatPopup').style.display = 'block';
}

function closeChat() {
  document.getElementById('chatPopup').style.display = 'none';
}

function startChat() {
  document.getElementById('chatStartScreen').style.display = 'none';
  document.getElementById('chatScreen').style.display = 'block';
}

function openResultsModal(title, html) {
  document.getElementById('resultsModalTitle').textContent = title;
  document.getElementById('resultsModalBody').innerHTML = html;
  document.getElementById('resultsModal').style.display = 'flex';
}

function closeResultsModal() {
  document.getElementById('resultsModal').style.display = 'none';
}

async function openStairsRequestModal() {
  const response = await fetch('/stairs-requests');
  const rows = await response.json();

  openResultsModal('Active STAIRS requests', renderTable(rows.filter(row => !row.response_date).slice(0, 10)));
}

async function openComplianceModal() {
  const response = await fetch('/properties-requiring-attention');
  const rows = await response.json();

  openResultsModal('Properties requiring attention', renderTable(rows.slice(0, 10)));
}

async function openNonCompliantModal() {
  const response = await fetch('/properties-requiring-attention');
  const rows = await response.json();

  const nonCompliantRows = rows.filter(row => row.compliance_status === 'Non-Compliant');

  openResultsModal('Non-compliant properties', renderTable(nonCompliantRows));
}

function closeStairsRequestModal() {
  document.getElementById('stairsRequestModal').style.display = 'none';
}

function closeComplianceModal() {
  document.getElementById('complianceModal').style.display = 'none';
}

function openNonCompliantModal() {
  document.getElementById('nonCompliantModal').style.display = 'block';
}

function closeNonCompliantModal() {
  document.getElementById('nonCompliantModal').style.display = 'none';
}
