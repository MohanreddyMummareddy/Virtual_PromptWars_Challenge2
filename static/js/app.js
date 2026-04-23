import ApiService from './apiService.js';
import UIManager from './uiManager.js';

document.addEventListener('DOMContentLoaded', () => {
    
    // Initialize specific modules (SOLID - Single Responsibility / Modularity principles)
    const api = new ApiService('/api/chat');
    const ui = new UIManager();
    
    // Application State
    let state = {
        zipCode: '',
        currentStopTitle: ''
    };

    // Bind onboarding events
    const startJourneyBtn = document.getElementById('start-journey-btn');
    const stateInput = document.getElementById('state-input');
    
    const handleStart = (e) => {
        if (e) e.preventDefault();
        
        const pincodeRegex = /^[1-9][0-9]{5}$/;
        const val = stateInput.value.trim();

        if(pincodeRegex.test(val)) {
            state.zipCode = val;
            console.log(`Starting journey for Zip: ${state.zipCode}`);
            ui.announce(`Loading your journey for ${state.zipCode}`);
            ui.showJourneyMap(state.zipCode);
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
        
        const loadingId = 'loading-' + Date.now();
        ui.addBotMessage("Thinking...", loadingId);

        try {
            const contextMsg = `User is at Zip Code ${state.zipCode}. They are asking about the subway stop: ${state.currentStopTitle}. Provide localized election info.`;
            const responseText = await api.fetchChatResponse(msg, contextMsg);
            
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

    // Business Logic Wrapper for opening panel
    function openAssistant(title, targetNodeId) {
        state.currentStopTitle = title;
        ui.openAssistantPanel(title, targetNodeId);
        
        let initialMsg = `Namaste! Welcome to the **${title}** stage of your voting journey in Pincode **${state.zipCode}**. I am your Indian Election Guide. How can I help you prepare?`;
        
        if (title.includes("Polling")) {
            initialMsg += " You can click below to find your designated Polling Station on Google Maps.";
        } else if (title.includes("Registration")) {
             initialMsg += " I can help you set a reminder for the registration deadline in your region.";
        }

        ui.addBotMessage(initialMsg);
    }
});
