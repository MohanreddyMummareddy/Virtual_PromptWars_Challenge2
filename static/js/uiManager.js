export default class UIManager {
    constructor() {
        this.cacheDOM();
    }

    cacheDOM() {
        this.onboardingScreen = document.getElementById('onboarding-screen');
        this.journeyScreen = document.getElementById('journey-screen');
        this.headerLocation = document.getElementById('header-location');
        this.nodes = document.querySelectorAll('.node');
        
        this.assistantPanel = document.getElementById('assistant-panel');
        this.closePanelBtn = document.getElementById('close-panel-btn');
        this.stopTitleDisplay = document.getElementById('stop-title-display');
        this.chatHistory = document.getElementById('chat-history');
        this.chatInput = document.getElementById('chat-input');
        this.calendarContainer = document.getElementById('calendar-link-container');
        
        // Accessibility Announcer
        this.ariaAnnouncer = document.getElementById('aria-live-announcer');
    }

    announce(message) {
        if (this.ariaAnnouncer) {
            this.ariaAnnouncer.textContent = message;
        }
    }

    showJourneyMap(state) {
        this.headerLocation.innerText = `My Civic Journey: ${state}`;
        this.onboardingScreen.classList.add('hidden');
        this.onboardingScreen.classList.remove('active');
        this.journeyScreen.classList.remove('hidden');
        this.journeyScreen.classList.add('active');
        
        // Accessibility focus shift
        this.headerLocation.focus();
        
        // Trigger path animation
        const animatedPath = document.querySelector('.animated-path');
        if (animatedPath) {
            animatedPath.style.animation = 'none';
            requestAnimationFrame(() => {
                animatedPath.style.animation = 'drawPath 2s linear forwards';
            });
        }
    }

    openAssistantPanel(title, targetNodeId, zipCode = '') {
        this.nodes.forEach(n => n.classList.remove('active'));
        const activeNode = document.querySelector(`[data-stop="${targetNodeId}"]`);
        if (activeNode) activeNode.classList.add('active');
        
        this.stopTitleDisplay.innerText = title;
        
        if (this.assistantPanel.classList.contains('hidden')) {
            this.assistantPanel.classList.remove('hidden');
            requestAnimationFrame(() => {
                this.assistantPanel.classList.add('show');
            });
        }
        
        this.clearChat();
        this.generateCalendarLinks(title, zipCode);
        
        // Accessibility
        this.announce(`${title} panel opened.`);
        this.chatInput.focus();
    }

    closeAssistantPanel() {
        this.assistantPanel.classList.remove('show');
        setTimeout(() => this.assistantPanel.classList.add('hidden'), 400);
        this.nodes.forEach(n => n.classList.remove('active'));
        this.announce("Assistant panel closed.");
    }

    clearChat() {
        this.chatHistory.innerHTML = '';
    }

    addUserMessage(text) {
        const div = this._createMessageNode(text, 'user-message');
        this.chatHistory.appendChild(div);
        this.scrollToBottom();
    }

    addBotMessage(text, id = null) {
        const div = this._createMessageNode(text, 'bot-message', true);
        if (id) div.id = id;
        this.chatHistory.appendChild(div);
        this.scrollToBottom();
        this.announce("New message from Civic Guide received.");
    }

    removeElement(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    scrollToBottom() {
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
    }

    _createMessageNode(text, className, isMarkup = false) {
        const div = document.createElement('div');
        div.className = `message ${className} scale-in`;
        
        if (isMarkup) {
            let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            formatted = formatted.replace(/\n/g, '<br>');
            formatted = formatted.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: var(--accent);">$1</a>');
            div.innerHTML = formatted;
        } else {
            div.innerText = text;
        }
        return div;
    }

    generateCalendarLinks(title, zipCode) {
        this.calendarContainer.innerHTML = '';
        
        const eventTitle = encodeURIComponent(`${title} Deadline`);
        const eventDetails = encodeURIComponent(`Reminder for ${title} process.`);
        
        const btn = document.createElement('button');
        btn.className = 'calendar-integration-btn';
        btn.id = 'sync-calendar-btn';
        btn.setAttribute('aria-label', `Add ${title} deadline to Google Calendar`);
        btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px;vertical-align:bottom;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg> Add to Google Calendar`;
        btn.style.display = "inline-block";
        btn.style.marginTop = "0.5rem";
        btn.style.fontSize = "0.8rem";
        btn.style.color = "#ffffff";
        btn.style.backgroundColor = "var(--accent)";
        btn.style.padding = "6px 12px";
        btn.style.borderRadius = "6px";
        btn.style.border = "none";
        btn.style.cursor = "pointer";
        btn.style.textDecoration = "none";
        btn.style.marginRight = "10px";
        
        const lowerTitle = title.toLowerCase();
        if(lowerTitle.includes("registration") || lowerTitle.includes("election") || lowerTitle.includes("deadline") || lowerTitle.includes("reminder")) {
            this.calendarContainer.appendChild(btn);
        }
        
        if (lowerTitle.includes("polling") || lowerTitle.includes("booth") || lowerTitle.includes("election") || lowerTitle.includes("station")) {
             const mapBtn = document.createElement('a');
             mapBtn.href = `https://www.google.com/maps/search/polling+booth+near+${zipCode}`;
             mapBtn.target = "_blank";
             mapBtn.setAttribute('aria-label', 'Find polling places near me on Google Maps');
             mapBtn.style.display = "inline-block";
             mapBtn.style.marginTop = "0.5rem";
             mapBtn.style.fontSize = "0.8rem";
             mapBtn.style.color = "#ffffff";
             mapBtn.style.backgroundColor = "#28a745";
             mapBtn.style.padding = "6px 12px";
             mapBtn.style.borderRadius = "6px";
             mapBtn.style.textDecoration = "none";
             mapBtn.style.cursor = "pointer";
             mapBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px;vertical-align:bottom;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg> Find on Google Maps`;
             this.calendarContainer.appendChild(mapBtn);
        }
    }
}
