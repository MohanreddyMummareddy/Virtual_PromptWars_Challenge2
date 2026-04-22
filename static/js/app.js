import ApiService from './apiService.js';
import UIManager from './uiManager.js';

document.addEventListener('DOMContentLoaded', () => {
    
    // Initialize specific modules (SOLID - Single Responsibility / Modularity principles)
    const api = new ApiService('/api/chat');
    const ui = new UIManager();
    
    // Application State
    let state = {
        userLocation: '',
        currentStopTitle: ''
    };

    // Bind onboarding events
    const startJourneyBtn = document.getElementById('start-journey-btn');
    const stateInput = document.getElementById('state-input');
    
    const handleStart = () => {
        if(stateInput.value.trim() !== '') {
            state.userLocation = stateInput.value.trim();
            ui.showJourneyMap(state.userLocation);
        } else {
            alert('Please enter your state to continue.');
            stateInput.focus();
        }
    };

    startJourneyBtn.addEventListener('click', handleStart);
    stateInput.addEventListener('keypress', (e) => {
        if(e.key === 'Enter') handleStart();
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
            const contextMsg = `User is in ${state.userLocation}. They are asking about the step: ${state.currentStopTitle}.`;
            const responseText = await api.fetchChatResponse(msg, contextMsg);
            
            ui.removeElement(loadingId);
            ui.addBotMessage(responseText);
        } catch (error) {
            ui.removeElement(loadingId);
            ui.addBotMessage(error.message);
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
        ui.addBotMessage(`Welcome to the **${title}** stop for **${state.userLocation}**. What questions do you have about this process?`);
    }
});
