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
            animatedPath.offsetHeight; /* trigger reflow */
            animatedPath.style.animation = 'drawPath 2s linear forwards';
        }
    }

    openAssistantPanel(title, targetNodeId) {
        this.nodes.forEach(n => n.classList.remove('active'));
        const activeNode = document.querySelector(`[data-stop="${targetNodeId}"]`);
        if (activeNode) activeNode.classList.add('active');
        
        this.stopTitleDisplay.innerText = title;
        
        if (this.assistantPanel.classList.contains('hidden')) {
            this.assistantPanel.classList.remove('hidden');
            void this.assistantPanel.offsetWidth; 
            this.assistantPanel.classList.add('show');
        }
        
        this.clearChat();
        this.generateCalendarLinks(title, "Your State");
        
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
            div.innerHTML = formatted;
        } else {
            div.innerText = text;
        }
        return div;
    }

    generateCalendarLinks(title, userState) {
        this.calendarContainer.innerHTML = '';
        
        const eventTitle = encodeURIComponent(`${title} Deadline`);
        const eventDetails = encodeURIComponent(`Reminder for ${title} process in ${userState}.`);
        
        const btn = document.createElement('a');
        btn.href = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${eventTitle}&details=${eventDetails}`;
        btn.target = "_blank";
        btn.className = 'calendar-integration-btn';
        btn.setAttribute('aria-label', `Add ${title} deadline to Google Calendar`);
        btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px;vertical-align:bottom;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg> Add to Google Calendar`;
        
        btn.style.display = "inline-block";
        btn.style.marginTop = "0.5rem";
        btn.style.fontSize = "0.8rem";
        btn.style.color = "var(--accent)";
        btn.style.textDecoration = "none";
        btn.style.marginRight = "10px";
        
        if(title.includes("Registration") || title.includes("Election Day") || title.includes("Deadlines")) {
            this.calendarContainer.appendChild(btn);
        }
        
        if (title.includes("Polling Place") || title.includes("Election Day")) {
             const mapBtn = document.createElement('a');
             mapBtn.href = `https://www.google.com/maps/search/polling+places+in+${userState}`;
             mapBtn.target = "_blank";
             mapBtn.setAttribute('aria-label', 'Find polling places near me on Google Maps');
             mapBtn.style.display = "inline-block";
             mapBtn.style.marginTop = "0.5rem";
             mapBtn.style.fontSize = "0.8rem";
             mapBtn.style.color = "#40c057";
             mapBtn.style.textDecoration = "none";
             mapBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px;vertical-align:bottom;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg> Find on Google Maps`;
             this.calendarContainer.appendChild(mapBtn);
        }
    }
}
