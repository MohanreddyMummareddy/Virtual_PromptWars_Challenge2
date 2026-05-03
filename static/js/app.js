import ApiService from './apiService.js';
import UIManager from './uiManager.js';

document.addEventListener('DOMContentLoaded', () => {
    
    // Initialize specific modules (SOLID - Single Responsibility / Modularity principles)
    const api = new ApiService('/api/chat');
    const ui = new UIManager();
    
    // Application State
    let state = {
        pincode: '',
        currentStopTitle: '',
        completedSteps: new Set()
    };

    // Bind onboarding events
    const startJourneyBtn = document.getElementById('start-journey-btn');
    const stateInput = document.getElementById('state-input');
    
    const handleStart = (e) => {
        if (e) e.preventDefault();
        
        const pincodeRegex = /^[1-9][0-9]{5}$/;
        const val = stateInput.value.trim();

        if(pincodeRegex.test(val)) {
            state.pincode = val;
            console.log(`Starting journey for Pincode: ${state.pincode}`);
            ui.announce(`Loading your journey for Pincode ${state.pincode}`);
            ui.showJourneyMap(state.pincode);
        } else {
            alert('Please enter a valid 6-digit Indian Pincode to continue.');
            stateInput.focus();
        }
    };

    if (startJourneyBtn) {
        startJourneyBtn.addEventListener('click', handleStart);
    }

    stateInput.addEventListener('keypress', (e) => {
        if(e.key === 'Enter') handleStart(e);
    });

    // Bind map nodes
    ui.nodes.forEach(node => {
        // Keyboard accessibility
        node.addEventListener('keydown', (e) => {
            if(e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const title = node.getAttribute('data-title');
                const stopId = node.getAttribute('data-stop');
                openAssistant(title, stopId);
            }
        });
        
        node.addEventListener('click', () => {
            const title = node.getAttribute('data-title');
            const stopId = node.getAttribute('data-stop');
            openAssistant(title, stopId);
        });
    });

    // Assistant close binding
    ui.closePanelBtn.addEventListener('click', () => ui.closeAssistantPanel());

    // Chat sending bindings
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatInput = document.getElementById('chat-input');

    const handleSendMessage = async () => {
        const msg = chatInput.value.trim();
        if(!msg) return;

        ui.addUserMessage(msg);
        chatInput.value = '';
        
        const lang = ui.getSelectedLanguage();
        const loadingId = 'loading-' + Date.now();
        ui.addBotMessage("Thinking...", loadingId);

        try {
            const contextMsg = `User is at Pincode ${state.pincode}. They are asking about the subway stop: ${state.currentStopTitle}. Provide localized Indian election info.`;
            let responseText = await api.fetchChatResponse(msg, contextMsg, lang);
            
            // Idea 4: Structured Output Parsing for Progress
            if (responseText.includes("PROGRESS_UPDATE:")) {
                const match = responseText.match(/PROGRESS_UPDATE:\s*\[?(.*?)\]?$/);
                if (match) {
                    const step = match[1].trim();
                    state.completedSteps.add(step);
                    ui.announce(`Milestone reached: ${step}`);
                    responseText = responseText.split("PROGRESS_UPDATE:")[0]; // Clean the UI
                }
            }
            
            ui.removeElement(loadingId);
            ui.addBotMessage(responseText);
        } catch (error) {
            console.error("Chat Error:", error);
            ui.removeElement(loadingId);
            const errorMsg = error.message.includes('503') ? "The AI service is currently warming up." : error.message;
            ui.addBotMessage(`⚠️ **Connection Issue:** ${errorMsg} Please try again.`);
        }
    };

    sendChatBtn.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if(e.key === 'Enter') handleSendMessage();
    });

    // Optimized Global Click Handler for Dynamic UI Elements
    document.addEventListener('click', async (e) => {
        // Handle Document Verification Trigger
        if (e.target && (e.target.id === 'verify-doc-btn' || e.target.closest('#verify-doc-btn'))) {
            document.getElementById('doc-upload').click();
            return;
        }

        // Handle Google Calendar Sync
        if (e.target && e.target.id === 'sync-calendar-btn') {
            ui.announce("Syncing with Google Calendar...");
            try {
                const response = await fetch('/api/calendar/invite', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        title: state.currentStopTitle, 
                        pincode: state.pincode 
                    })
                });
                const data = await response.json();
                if (data.link) {
                    window.open(data.link, '_blank');
                    ui.addBotMessage(`✅ **Calendar Sync:** Event created! Opening in a new tab...`);
                } else {
                    ui.addBotMessage(`⚠️ **Calendar Sync Error:** ${data.error || "Failed to create event."}`);
                }
            } catch (err) {
                ui.addBotMessage("⚠️ Failed to sync with Google Calendar API.");
            }
        }
    });

    // Handle Document Upload Change
    document.addEventListener('change', async (e) => {
        if (e.target && e.target.id === 'doc-upload') {
            const file = e.target.files[0];
            if (!file) return;

            ui.addBotMessage("🔍 Analyzing your document...");
            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/api/verify-document', { method: 'POST', body: formData });
                const data = await res.json();
                ui.addBotMessage(`📄 **Document Analysis:** ${data.analysis}`);
            } catch (err) {
                ui.addBotMessage("⚠️ Verification failed. Please try a clearer photo.");
            }
        }

        // Handle Wallet Pass Generation
        if (e.target && e.target.id === 'save-wallet-btn') {
            ui.announce("Generating your Civic Hero Pass...");
            try {
                const res = await fetch('/api/wallet/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pincode: state.pincode })
                });
                const data = await res.json();
                if (data.url) {
                    window.open(data.url, '_blank');
                    ui.addBotMessage("🌟 **Success!** Your Civic Hero badge is ready to be saved to your Google Wallet.");
                }
            } catch (err) {
                ui.addBotMessage("⚠️ Could not generate Wallet pass at this time.");
            }
        }
    });

    // Business Logic Wrapper for opening panel
    function openAssistant(title, targetNodeId) {
        state.currentStopTitle = title;
        ui.openAssistantPanel(title, targetNodeId, state.pincode);

        let initialMsg = `Namaste! Welcome to the **${title}** stage of your voting journey in Pincode **${state.pincode}**. I am your Indian Election Guide. How can I help you prepare?`;
        
        if (title.includes("Polling")) {
            initialMsg += " You can click below to find your designated Polling Station on Google Maps.";
        } else if (title.includes("Registration")) {
             initialMsg += " I can help you set a reminder for the registration deadline in your region.";
        }

        ui.addBotMessage(initialMsg);
    }
});
